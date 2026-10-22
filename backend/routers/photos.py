"""Photo upload, deletion and same-origin media serving."""
from __future__ import annotations

import os
import sqlite3
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile, status
from fastapi.responses import FileResponse

from backend.db import get_db
from backend.errors import ApiError, PayloadTooLargeError
from backend.models import PhotoUploadResult
from backend.storage import files
from backend.storage import trips as trip_store
from backend.storage.images import ImageValidationError, process_image

router = APIRouter(tags=["photos"])

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/octet-stream",
}

CHUNK = 1024 * 1024


@router.post(
    "/api/trips/{trip_id}/photos",
    response_model=PhotoUploadResult,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    request: Request,
    trip_id: str,
    file: UploadFile = File(...),
    alt: str = Form(""),
    connection: sqlite3.Connection = Depends(get_db),
) -> dict:
    settings = request.app.state.settings
    if len(alt) > 200:
        raise ApiError("Photo description must be 200 characters or fewer.", status_code=422, code="validation_error")
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ApiError("Choose a JPEG, PNG or WebP photograph.", status_code=415, code="unsupported_media")
    if not trip_store.trip_exists(connection, trip_id):
        raise ApiError("This trip does not exist.", status_code=404, code="trip_not_found")
    if trip_store.photo_count(connection, trip_id) >= settings.max_photos_per_trip:
        raise ApiError(
            f"Each trip can hold at most {settings.max_photos_per_trip} photographs.",
            status_code=422,
            code="photo_limit_reached",
        )

    upload_fd, upload_name = tempfile.mkstemp(dir=settings.tmp_dir, prefix="upload-", suffix=".bin")
    os.close(upload_fd)
    upload_path = Path(upload_name)
    staged_path = Path(settings.tmp_dir) / f"{uuid.uuid4()}.out"
    final_name: str | None = None
    inserted = False

    try:
        total = 0
        with upload_path.open("wb") as target:
            while chunk := await file.read(CHUNK):
                total += len(chunk)
                if total > settings.max_upload_bytes:
                    raise PayloadTooLargeError(
                        f"Photographs must be {settings.max_upload_bytes // (1024 * 1024)} MB or smaller."
                    )
                target.write(chunk)
        if total == 0:
            raise ApiError("The uploaded file is empty.", status_code=422, code="invalid_image")

        try:
            processed = process_image(
                upload_path,
                staged_path,
                max_edge=settings.stored_max_edge,
                min_edge=settings.min_image_edge,
                max_pixels=settings.max_image_pixels,
                jpeg_quality=settings.stored_jpeg_quality,
            )
        except ImageValidationError as exc:
            raise ApiError(exc.message, status_code=exc.status_code, code=exc.code) from exc

        final_name = f"{uuid.uuid4()}{processed.extension}"
        photo = trip_store.add_photo(
            connection,
            trip_id=trip_id,
            filename=final_name,
            alt=alt,
            mime=processed.mime,
            width=processed.width,
            height=processed.height,
            size=processed.bytes,
            max_photos=settings.max_photos_per_trip,
        )
        inserted = True
        try:
            files.atomic_install(staged_path, Path(settings.media_dir) / final_name)
        except OSError as exc:
            trip_store.remove_photo_row_by_filename(connection, final_name)
            inserted = False
            raise ApiError(
                "The photograph could not be stored on this computer.",
                status_code=500,
                code="storage_error",
            ) from exc
        return photo
    finally:
        if inserted and final_name:
            # A later failure must not leave a row without a usable file.
            if not (Path(settings.media_dir) / final_name).is_file():
                trip_store.remove_photo_row_by_filename(connection, final_name)
        files.unlink_quiet(upload_path)
        files.unlink_quiet(staged_path)
        await file.close()


@router.delete("/api/trips/{trip_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    trip_id: str,
    photo_id: str,
    request: Request,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    filename = trip_store.remove_photo(connection, trip_id, photo_id)
    files.unlink_quiet(Path(request.app.state.settings.media_dir) / filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/media/{filename}")
def read_media(
    filename: str,
    request: Request,
    connection: sqlite3.Connection = Depends(get_db),
) -> FileResponse:
    settings = request.app.state.settings
    path = files.media_path(settings.media_dir, filename)
    row = connection.execute("SELECT mime FROM photos WHERE filename = ?", (filename,)).fetchone()
    if row is None or not path.is_file():
        raise ApiError("Media file not found.", status_code=404, code="not_found")
    return FileResponse(
        path,
        media_type=row["mime"],
        headers={
            "Cache-Control": "private, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )
