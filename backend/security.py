"""Security headers, dotfile blocking and request logging."""
from __future__ import annotations

import logging
import time
from urllib.parse import urlsplit

from fastapi import FastAPI, Request

from backend.errors import error_response

logger = logging.getLogger("travel_memory_map.backend")

CSP = (
    "default-src 'self'; "
    "script-src 'self' https://*.googleapis.com https://*.gstatic.com blob:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "img-src 'self' data: blob: https://*.googleapis.com https://*.gstatic.com "
    "https://*.google.com https://*.googleusercontent.com https://tiles.openfreemap.org; "
    "connect-src 'self' https://*.googleapis.com https://*.gstatic.com https://*.google.com https://tiles.openfreemap.org data: blob:; "
    "font-src 'self' https://fonts.gstatic.com https://tiles.openfreemap.org; "
    "worker-src blob:; "
    "frame-src https://*.google.com; "
    "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
)


# Google Maps' documented CSP needs eval. Keep that exception off ordinary pages.
GOOGLE_CSP = CSP.replace("script-src 'self'", "script-src 'self' 'unsafe-eval'")


def origin_tuple(value: str):
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            return None
        return parsed.scheme, parsed.hostname.lower(), parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return None


def install_security(app: FastAPI) -> None:
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        settings = app.state.settings
        allowed_hosts = {"localhost", "127.0.0.1", "::1"}
        if settings.host not in {"0.0.0.0", "::"}:
            allowed_hosts.add(settings.host.lower())
        target = origin_tuple(str(request.url))
        if target is None or target[1] not in allowed_hosts:
            return error_response(403, "invalid_host", "This local service does not accept this host.")
        origin = request.headers.get("origin")
        if origin is not None and origin_tuple(origin) != target:
            return error_response(403, "forbidden_origin", "Cross-origin requests are not allowed.")
        if request.method not in {"GET", "HEAD", "OPTIONS"} and request.headers.get("sec-fetch-site") == "cross-site":
            return error_response(403, "forbidden_origin", "Cross-site changes are not allowed.")
        parts = [part for part in request.url.path.split("/") if part]
        if any(part.startswith(".") for part in parts):
            return error_response(404, "not_found", "Not found.")

        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - started) * 1000

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        policy = GOOGLE_CSP if request.url.path in {"/app/", "/app/index.html"} and request.query_params.get("map") == "google" else CSP
        response.headers.setdefault("Content-Security-Policy", policy)
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
