#!/usr/bin/env bash
set -euo pipefail

# Reset R2R Postgres schema and align embedding dimension to 2560.
# - Updates both [embedding] and [completion_embedding] base_dimension in py/r2r/r2r.toml
# - Drops the existing Postgres schema (destructive)
# - Restarts Docker containers if present (r2r_postgres, r2r_app)
# - Verifies the vector dimension for the new schema
#
# Usage:
#   chmod +x scripts/reset_schema_to_2560.sh
#   scripts/reset_schema_to_2560.sh
#
# Optional env vars (override defaults):
#   PROJECT_NAME           - R2R schema name (defaults to value in r2r.toml or r2r_local)
#   DIMENSION              - Embedding dimension (default 2560)
#   DB_HOST, DB_PORT       - Postgres host/port (default 127.0.0.1:5432)
#   DB_USER, DB_PASSWORD   - Postgres user/password (default r2r/r2rpassword)
#   DB_NAME                - Postgres database name (default r2r)

here() { cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd; }
ROOT_DIR="$(here)"
cd "$ROOT_DIR"

TOML_PATH="py/r2r/r2r.toml"
DIMENSION="${DIMENSION:-2560}"

# Extract project name from TOML [app] section; fallback to env or default
extract_project_name() {
  awk '
    BEGIN { in_app=0; project="" }
    /^\[app\]/ { in_app=1; next }
    /^\[/ { in_app=0 }
    in_app && $0 ~ /project_name/ {
      match($0, /project_name\s*=\s*"([^"]+)"/, m)
      if (m[1] != "") { project=m[1]; print project; exit }
    }
  ' "$TOML_PATH"
}

PROJECT_NAME_DEFAULT="r2r_local"
PROJECT_NAME="${PROJECT_NAME:-$(extract_project_name || true)}"
PROJECT_NAME="${PROJECT_NAME:-$PROJECT_NAME_DEFAULT}"

log() { echo "[reset] $*"; }
warn() { echo "[reset][WARN] $*" >&2; }
err() { echo "[reset][ERROR] $*" >&2; }

# Update base_dimension in both [embedding] and [completion_embedding]
update_dimensions_in_toml() {
  if [[ ! -f "$TOML_PATH" ]]; then
    err "TOML not found at $TOML_PATH"
    exit 1
  fi
  log "Setting base_dimension=$DIMENSION in [embedding] and [completion_embedding]"
  # Within section [embedding]
  sed -i -E \
    "/^\[embedding\]/,/^\[/ s/^(\s*base_dimension\s*=).*/\1 ${DIMENSION}/" \
    "$TOML_PATH"
  # Within section [completion_embedding]
  sed -i -E \
    "/^\[completion_embedding\]/,/^\[/ s/^(\s*base_dimension\s*=).*/\1 ${DIMENSION}/" \
    "$TOML_PATH"
}

container_exists() {
  docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^$1$" || return 1
}

drop_schema_with_docker() {
  local schema="$1" user="$2" pass="$3" db="$4"
  if ! container_exists r2r_postgres; then
    return 1
  fi
  log "Dropping schema \"$schema\" via docker exec into r2r_postgres"
  docker exec -e PGPASSWORD="$pass" r2r_postgres \
    psql -h 127.0.0.1 -U "$user" -d "$db" -v ON_ERROR_STOP=1 \
    -c "DROP SCHEMA IF EXISTS \"$schema\" CASCADE;"
}

drop_schema_with_psql() {
  local host="$1" port="$2" user="$3" pass="$4" db="$5" schema="$6"
  if ! command -v psql >/dev/null 2>&1; then
    err "psql not found and docker container r2r_postgres not running. Install psql or run docker."
    exit 1
  fi
  log "Dropping schema \"$schema\" via psql on $host:$port"
  PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -v ON_ERROR_STOP=1 \
    -c "DROP SCHEMA IF EXISTS \"$schema\" CASCADE;"
}

restart_app_container_if_present() {
  if container_exists r2r_app; then
    log "Restarting r2r_app container"
    docker restart r2r_app >/dev/null
  else
    warn "Container r2r_app not running. Please restart your app manually."
  fi
}

verify_dimension() {
  local expect_dim="$1" host="$2" port="$3" user="$4" pass="$5" db="$6" schema="$7"
  local q
  q="SELECT a.atttypmod as dimension\n\
     FROM pg_attribute a\n\
     JOIN pg_class c ON a.attrelid = c.oid\n\
     JOIN pg_namespace n ON c.relnamespace = n.oid\n\
     WHERE n.nspname = '$schema' AND c.relname = 'chunks' AND a.attname = 'vec';"

  local attempt=0 max_attempts=30
  while (( attempt < max_attempts )); do
    if container_exists r2r_postgres; then
      out=$(docker exec -e PGPASSWORD="$pass" r2r_postgres \
        psql -h 127.0.0.1 -U "$user" -d "$db" -tA -c "$q" 2>/dev/null || true)
    else
      out=$(PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$db" -tA -c "$q" 2>/dev/null || true)
    fi
    if [[ "$out" == "$expect_dim" ]]; then
      log "Verified chunks.vec dimension = $expect_dim"
      return 0
    fi
    ((attempt++))
    sleep 2
  done
  warn "Could not verify dimension=$expect_dim after $((max_attempts*2))s. The app may not have recreated tables yet."
}

main() {
  # Defaults mirror docker/compose.dev.yaml
  DB_HOST="${DB_HOST:-127.0.0.1}"
  DB_PORT="${DB_PORT:-5432}"
  DB_USER="${DB_USER:-r2r}"
  DB_PASSWORD="${DB_PASSWORD:-r2rpassword}"
  DB_NAME="${DB_NAME:-r2r}"

  log "Project name: $PROJECT_NAME"
  log "Target dimension: $DIMENSION"

  update_dimensions_in_toml

  # Drop schema either via docker or local psql
  if ! drop_schema_with_docker "$PROJECT_NAME" "$DB_USER" "$DB_PASSWORD" "$DB_NAME"; then
    drop_schema_with_psql "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$PROJECT_NAME"
  fi

  # Restart app container if present so it recreates tables
  restart_app_container_if_present

  # Attempt to verify new dimension
  verify_dimension "$DIMENSION" "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$PROJECT_NAME"

  log "Done. If you did not use Docker, restart your app so it recreates the schema, then re-ingest documents."
}

main "$@"

