"""Read-only AI memory proxy.

The route never writes to the database. It sends only the selected trip after
an explicit confirmation and returns either a draft or a clarification request.
"""
from __future__ import annotations

import asyncio
import logging
import sqlite3
import tempfile
import time
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from starlette.concurrency import run_in_threadpool

from backend.ai import generator_configured
from backend.ai.base import MemoryRequest, MemoryResult, ProviderError, ProviderUnavailable
from backend.db import get_db
from backend.errors import ApiError
from backend.models import MemoryRequestIn
from backend.storage import trips as trip_store
from backend.storage.images import ImageValidationError, process_image

logger = logging.getLogger("travel_memory_map.backend")

router = APIRouter(tags=["memory"])


@router.post("/api/trips/{trip_id}/memory", response_model=MemoryResult)
async def request_memory(
    request: Request,
    trip_id: str,
    payload: MemoryRequestIn,
    connection: sqlite3.Connection = Depends(get_db),
) -> MemoryResult:
    if not payload.confirmed:
        raise ApiError(
            "Confirm the pre-send notice before requesting an AI draft.",
            status_code=400,
            code="confirmation_required",
        )

    settings = request.app.state.settings
    snapshot = trip_store.get_snapshot(connection, trip_id)
    city = request.app.state.cities.get(snapshot["city_id"])
    if city is None:
        raise ApiError("This trip's city is no longer supported.", status_code=500, code="unknown_city")

    generator = request.app.state.generator
    if not generator_configured(generator):
        raise ApiError(
            "No AI provider is configured on this local backend.",
            status_code=503,
            code="ai_not_configured",
        )

    filenames = trip_store.list_photo_filenames(connection, trip_id)
    started = time.perf_counter()

    with tempfile.TemporaryDirectory(dir=settings.tmp_dir, prefix="ai-") as folder:
        copies: list[Path] = []
        for index, filename in enumerate(filenames):
            source = Path(settings.media_dir) / filename
            destination = Path(folder) / f"{index}.jpg"
            try:
                await run_in_threadpool(
                    process_image,
                    source,
                    destination,
                    max_edge=settings.ai_max_edge,
                    min_edge=1,
                    max_pixels=settings.max_image_pixels,
                    jpeg_quality=settings.ai_jpeg_quality,
                    force_jpeg=True,
                )
            except ImageValidationError as exc:
                raise ApiError(
                    "A stored photograph could not be prepared for the AI request.",
                    status_code=500,
                    code="storage_error",
                ) from exc
            copies.append(destination)

        ai_request = MemoryRequest(
            city_name=city.name,
            trip_date=snapshot["trip_date"],
            title=snapshot["title"],
            notes=snapshot["notes"],
            photo_paths=tuple(copies),
        )

        try:
            result = await asyncio.wait_for(
                generator.generate(ai_request),
                timeout=settings.ai_timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            logger.warning("AI request for trip %s timed out", trip_id)
            raise ApiError(
                "The AI request timed out. Your saved trip is unchanged.",
                status_code=504,
                code="ai_timeout",
            ) from exc
        except ProviderUnavailable as exc:
            raise ApiError(
                "No AI provider is configured on this local backend.",
                status_code=503,
                code="ai_not_configured",
            ) from exc
        except ProviderError as exc:
            logger.warning("AI provider failed for trip %s: %s", trip_id, exc)
            raise ApiError(
                "The AI provider could not complete this request. Your saved trip is unchanged.",
                status_code=502,
                code="ai_provider_error",
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected AI failure for trip %s", trip_id)
            raise ApiError(
                "The AI provider could not complete this request. Your saved trip is unchanged.",
                status_code=502,
                code="ai_provider_error",
            ) from exc

    try:
        if not isinstance(result, MemoryResult):
            result = MemoryResult.model_validate(result)
    except Exception as exc:
        logger.warning("AI provider returned malformed output for trip %s", trip_id)
        raise ApiError(
            "The AI provider returned an unusable response. Your saved trip is unchanged.",
            status_code=502,
            code="ai_malformed_response",
        ) from exc

    if result.status == "draft" and (not result.title.strip() or not result.text.strip()):
        logger.warning("AI draft for trip %s was empty", trip_id)
        raise ApiError(
            "The AI provider returned an unusable response. Your saved trip is unchanged.",
            status_code=502,
            code="ai_malformed_response",
        )
    if result.status == "clarification" and not (result.question or "").strip():
        logger.warning("AI clarification for trip %s had no question", trip_id)
        raise ApiError(
            "The AI provider returned an unusable response. Your saved trip is unchanged.",
            status_code=502,
            code="ai_malformed_response",
        )
    if result.status == "refusal" and (
        result.title.strip() or result.text.strip() or not (result.warning or "").strip()
    ):
        logger.warning("AI refusal for trip %s contained a draft or had no reason", trip_id)
        raise ApiError(
            "The AI provider returned an unusable response. Your saved trip is unchanged.",
            status_code=502,
            code="ai_malformed_response",
        )

    logger.info(
        "AI request for trip %s via %s finished as %s in %.0f ms",
        trip_id,
        getattr(generator, "name", "unknown"),
        result.status,
        (time.perf_counter() - started) * 1000,
    )
    return result
