"""One JSON error envelope for every API failure."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("travel_memory_map.backend")


class ApiError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = list(details or [])


class NotFoundError(ApiError):
    status_code = 404
    code = "not_found"


class BadRequestError(ApiError):
    status_code = 400
    code = "bad_request"


class PayloadTooLargeError(ApiError):
    status_code = 413
    code = "file_too_large"


class UnsupportedMediaError(ApiError):
    status_code = 415
    code = "unsupported_media"


def error_payload(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_payload(code, message, details),
        headers=headers,
    )


_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    413: "file_too_large",
    415: "unsupported_media",
    422: "validation_error",
    500: "internal_error",
    502: "ai_provider_error",
    503: "service_unavailable",
    504: "ai_timeout",
}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("%s %s failed: %s", request.method, request.url.path, exc.code)
        else:
            logger.warning("%s %s returned %s: %s", request.method, request.url.path, exc.status_code, exc.code)
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "loc": ".".join(str(part) for part in item.get("loc", ())),
                "msg": item.get("msg", "Invalid value"),
                "type": item.get("type", "value_error"),
            }
            for item in exc.errors()
        ]
        return error_response(422, "validation_error", "Request validation failed.", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _STATUS_CODES.get(exc.status_code, "http_error")
        message = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return error_response(exc.status_code, code, message, headers=exc.headers)

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error for %s %s", request.method, request.url.path)
        return error_response(500, "internal_error", "The local backend could not complete this request.")
