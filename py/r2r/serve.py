import argparse
import asyncio
import logging
import os
import sys
from typing import Optional

try:  # Python 3.11+
    import tomllib as tomli  # type: ignore
except Exception:  # pragma: no cover
    tomli = None  # type: ignore

logger = logging.getLogger(__name__)

try:
    from core import R2RApp, R2RBuilder, R2RConfig
    from core.utils.logging_config import configure_logging
except ImportError as e:
    logger.error(
        f"Failed to start server: core dependencies not installed: {e}"
    )
    logger.error("To run the server, install the required dependencies:")
    logger.error("pip install 'r2r[core]'")
    sys.exit(1)


async def create_app(
    config_name: Optional[str] = None,
    config_path: Optional[str] = None,
    full: bool = False,
) -> "R2RApp":
    """
    Creates and returns an R2R application instance based on the provided
    or environment-sourced configuration.
    """
    # If arguments not passed, fall back to environment variables
    config_name = config_name or os.getenv("R2R_CONFIG_NAME")
    config_path = config_path or os.getenv("R2R_CONFIG_PATH")

    if config_path and config_name:
        raise ValueError(
            f"Cannot specify both config_path and config_name, got {config_path} and {config_name}"
        )

    if not config_path and not config_name:
        # If neither is specified nor set in environment,
        # default to 'full' if --full is True, else 'default'
        config_name = "full" if full else "default"

    try:
        r2r_instance = await R2RBuilder(
            config=R2RConfig.load(config_name, config_path)
        ).build()

        # Start orchestration worker
        await r2r_instance.orchestration_provider.start_worker()
        return r2r_instance
    except ImportError as e:
        logger.error(f"Failed to initialize R2R: {e}")
        logger.error(
            "Please check your configuration and installed dependencies"
        )
        sys.exit(1)


def run_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    config_name: Optional[str] = None,
    config_path: Optional[str] = None,
    full: bool = False,
):
    """
    Runs the R2R server with the provided or environment-based settings.
    """
    # Overwrite environment variables if arguments are explicitly passed
    if host is not None:
        os.environ["R2R_HOST"] = host
    if port is not None:
        os.environ["R2R_PORT"] = str(port)
    if config_path is not None:
        os.environ["R2R_CONFIG_PATH"] = config_path
    if config_name is not None:
        os.environ["R2R_CONFIG_NAME"] = config_name

    # Fallback to environment or defaults if necessary
    final_host = os.getenv("R2R_HOST", "0.0.0.0")
    final_port = int(os.getenv("R2R_PORT", "8002"))

    try:
        configure_logging()
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")

    # Load select env vars from r2r.toml (do not override already-set env)
    def _load_env_from_toml(cfg_path: Optional[str]):
        path_candidates: list[str] = []
        if cfg_path:
            path_candidates.append(cfg_path)
        # Default to package r2r.toml if present
        path_candidates.append(os.path.join(os.path.dirname(__file__), "r2r.toml"))
        # Also try CWD
        path_candidates.append(os.path.join(os.getcwd(), "py", "r2r", "r2r.toml"))
        path_candidates.append(os.path.join(os.getcwd(), "r2r.toml"))

        existing_path = next((p for p in path_candidates if os.path.isfile(p)), None)
        if not existing_path:
            logger.info("No r2r.toml found for env loading; skipping.")
            return
        if not tomli:
            logger.warning("tomllib/tomli not available; cannot load env from TOML.")
            return

        try:
            with open(existing_path, "rb") as f:
                data = tomli.load(f)  # type: ignore
        except Exception as e:
            logger.warning(f"Failed to parse {existing_path}: {e}")
            return

        # Map TOML fields to environment variables
        mappings: list[tuple[str, Optional[str]]] = []
        app = data.get("app", {}) if isinstance(data, dict) else {}
        db = data.get("database", {}) if isinstance(data, dict) else {}
        embedding = data.get("embedding", {}) if isinstance(data, dict) else {}

        # Project name
        if app:
            mappings.append(("R2R_PROJECT_NAME", app.get("project_name")))

        # Database
        if db:
            mappings.extend(
                [
                    ("R2R_POSTGRES_HOST", db.get("host")),
                    ("R2R_POSTGRES_PORT", str(db.get("port")) if db.get("port") is not None else None),
                    ("R2R_POSTGRES_USER", db.get("user")),
                    ("R2R_POSTGRES_PASSWORD", db.get("password")),
                    ("R2R_POSTGRES_DBNAME", db.get("db_name")),
                ]
            )

        # Embeddings via OpenAI-compatible server (used by litellm)
        if embedding:
            mappings.extend(
                [
                    ("OPENAI_API_BASE", embedding.get("OPENAI_API_BASE")),
                    ("OPENAI_API_KEY", embedding.get("OPENAI_API_KEY")),
                    ("OPENAI_API_LIKE_BASE", embedding.get("OPENAI_API_LIKE_BASE")),
                    ("OPENAI_API_LIKE_KEY", embedding.get("OPENAI_API_LIKE_KEY")),
                ]
            )

        set_count = 0
        for key, val in mappings:
            if val and not os.getenv(key):
                os.environ[key] = str(val)
                set_count += 1
        logger.info(
            f"Loaded {set_count} environment variables from {os.path.basename(existing_path)} (non-destructive)."
        )

    try:

        async def start():
            # Ensure env is populated from TOML before building the app
            _load_env_from_toml(config_path)
            app = await create_app(config_name, config_path, full)
            await app.serve(final_host, final_port)

        asyncio.run(start())
    except Exception as e:
        logger.error(f"Failed to start R2R server: {e}")
        raise e
        sys.exit(1)


def main():
    """
    Parse command-line arguments and then run the server.
    """
    parser = argparse.ArgumentParser(description="Run the R2R server.")
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to. Overrides R2R_HOST env if provided.",
    )
    parser.add_argument(
        "--port",
        default=None,
        type=int,
        help="Port to bind to. Overrides R2R_PORT env if provided.",
    )
    parser.add_argument(
        "--config-path",
        default=None,
        help="Path to the configuration file. Overrides R2R_CONFIG_PATH env if provided.",
    )
    parser.add_argument(
        "--config-name",
        default=None,
        help="Name of the configuration. Overrides R2R_CONFIG_NAME env if provided.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use the 'full' config if neither config-path nor config-name is specified.",
    )

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        config_name=args.config_name,
        config_path=args.config_path,
        full=args.full,
    )


if __name__ == "__main__":
    main()
