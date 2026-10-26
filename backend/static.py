"""Serve the existing static application from the same origin as the API."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config import Settings


def install_static(app: FastAPI, settings: Settings) -> None:
    app_dir = settings.app_dir
    data_dir = settings.data_dir
    if not app_dir.is_dir():
        raise RuntimeError(f"Application directory not found at {app_dir}.")
    if not data_dir.is_dir():
        raise RuntimeError(f"Data directory not found at {data_dir}.")

    # Runtime state (SQLite, uploads) lives outside these two mounts by design.
    app.mount("/app", StaticFiles(directory=str(app_dir), html=True), name="app")
    app.mount("/data", StaticFiles(directory=str(data_dir), html=True), name="data")

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse("/app/", status_code=302)
