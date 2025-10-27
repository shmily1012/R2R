#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export R2R_CONFIG_PATH="${PROJECT_ROOT}/py/r2r/configs/ddr4.toml"
export R2R_PORT="${R2R_PORT:-8003}"
unset R2R_CONFIG_NAME || true

exec python -m r2r.serve "$@"
