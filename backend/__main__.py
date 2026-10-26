"""Canonical launcher: ``python3 -m backend``."""
from __future__ import annotations

import argparse
import logging
from dataclasses import replace

import uvicorn

from backend.app import create_app
from backend.config import Settings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the local Travel Memory Map backend.")
    parser.add_argument("--host", default=None, help="Bind address (default 127.0.0.1).")
    parser.add_argument("--port", type=int, default=None, help="Port (default 8019).")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    settings = Settings.from_env()
    if args.host:
        settings = replace(settings, host=args.host)
    if args.port:
        settings = replace(settings, port=args.port)

    application = create_app(settings)
    print(
        f"Travel Memory Map backend: http://{settings.host}:{settings.port}/app/?mode=api "
        "(Ctrl+C to stop)",
        flush=True,
    )
    uvicorn.run(application, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
