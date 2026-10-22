"""Health and local-only Maps configuration."""
from __future__ import annotations

import os
import sqlite3
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from backend.ai import generator_configured
from backend.config import connect_allowed_hosts
from backend.db import get_db
from backend.errors import ApiError
from map_config import read_map_config

router = APIRouter(tags=["system"])


@router.get("/api/health")
def health(request: Request, connection: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    settings = request.app.state.settings
    database = "ok"
    try:
        connection.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        database = "unavailable"
    media = "ok" if settings.media_dir.is_dir() and os.access(settings.media_dir, os.W_OK) else "unavailable"
    storage_ok = database == "ok" and media == "ok"
    body = {
        "status": "ok" if storage_ok else "degraded",
        "storage": {"database": database, "media": media},
        "ai_configured": generator_configured(request.app.state.generator),
    }
    if not storage_ok:
        body["error"] = {
            "code": "storage_unavailable",
            "message": "The local album storage is not writable.",
        }
    return JSONResponse(body, status_code=200 if storage_ok else 503)


@router.get("/api/map-config")
def map_config(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    allowed = connect_allowed_hosts(settings)
    host = request.headers.get("host")
    origin = request.headers.get("origin")
    if host not in allowed or (origin and urlsplit(origin).netloc not in allowed):
        raise ApiError(
            "This endpoint is only available on the local preview.",
            status_code=403,
            code="forbidden_origin",
        )
    return read_map_config(settings.root)
