"""Security headers, dotfile blocking and request logging."""
from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request

from backend.errors import error_response

logger = logging.getLogger("travel_memory_map.backend")

CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-eval' https://*.googleapis.com https://*.gstatic.com blob:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "img-src 'self' data: blob: https://*.googleapis.com https://*.gstatic.com "
    "https://*.google.com https://*.googleusercontent.com; "
    "connect-src 'self' https://*.googleapis.com https://*.gstatic.com https://*.google.com data: blob:; "
    "font-src 'self' https://fonts.gstatic.com; "
    "worker-src blob:; "
    "frame-src https://*.google.com; "
    "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
)


def install_security(app: FastAPI) -> None:
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        parts = [part for part in request.url.path.split("/") if part]
        if any(part.startswith(".") for part in parts):
            return error_response(404, "not_found", "Not found.")

        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started) * 1000

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Content-Security-Policy", CSP)
        if not response.headers.get("Cache-Control"):
            response.headers["Cache-Control"] = "no-store"

        path = request.url.path
        if path.startswith("/api"):
            logger.info(
                "%s %s -> %s (%.1f ms)",
                request.method,
                path,
                response.status_code,
                duration_ms,
            )
        elif response.status_code >= 400:
            logger.warning("%s %s -> %s", request.method, path, response.status_code)
        return response
