"""Trip and photo SQL.

A trip row is the single visit identity. Photo rows never affect the count, and
only ``POST /api/trips`` inserts a trip, so an edit cannot create a visit.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.errors import ApiError

TRIP_ORDER = (
    "CASE WHEN trip_date IS NULL THEN 1 ELSE 0 END, "
    "trip_date DESC, created_at DESC, id DESC"
)

EDITABLE_COLUMNS = {"title", "notes", "memory_text", "trip_date"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _photo_preview(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "url": f"/media/{row['filename']}",
        "alt": row["alt"],
    }


def _trip_dict(row: sqlite3.Row, photos: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "city_id": row["city_id"],
        "trip_date": row["trip_date"],
        "title": row["title"],
        "notes": row["notes"],
        "memory_text": row["memory_text"],
        "photos": photos,
        "source": row["source"],
    }


def list_snapshots(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    """One query for trips and one for photos; no N+1 lookups."""
    trips = connection.execute(f"SELECT * FROM trips ORDER BY {TRIP_ORDER}").fetchall()
    photos = connection.execute(
        "SELECT * FROM photos ORDER BY trip_id, position, created_at"
    ).fetchall()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for photo in photos:
        grouped.setdefault(photo["trip_id"], []).append(_photo_preview(photo))
    return [_trip_dict(row, grouped.get(row["id"], [])) for row in trips]


def get_snapshot(connection: sqlite3.Connection, trip_id: str) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if row is None:
        raise ApiError("This trip does not exist.", status_code=404, code="trip_not_found")
    photos = connection.execute(
        "SELECT * FROM photos WHERE trip_id = ? ORDER BY position, created_at", (trip_id,)
    ).fetchall()
    return _trip_dict(row, [_photo_preview(photo) for photo in photos])


def create_trip(
    connection: sqlite3.Connection,
    *,
    city_id: str,
    trip_date: str | None,
    title: str,
    notes: str,
) -> dict[str, Any]:
    trip_id = str(uuid.uuid4())
    timestamp = now_iso()
    with connection:
        connection.execute(
            """
            INSERT INTO trips
              (id, city_id, trip_date, title, notes, memory_text, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, '', 'user', ?, ?)
            """,
            (trip_id, city_id, trip_date, title, notes, timestamp, timestamp),
        )
    return get_snapshot(connection, trip_id)


def update_trip(connection: sqlite3.Connection, trip_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    if not patch:
        raise ApiError("Provide at least one field to update.", status_code=422, code="validation_error")
    unexpected = set(patch) - EDITABLE_COLUMNS
    if unexpected:
        raise ApiError(
            "Only title, notes, memory_text and trip_date can be edited.",
            status_code=422,
            code="validation_error",
        )
    row = connection.execute("SELECT 1 FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if row is None:
        raise ApiError("This trip does not exist.", status_code=404, code="trip_not_found")

    values = dict(patch)
    values["updated_at"] = now_iso()
    assignments = ", ".join(f"{column} = ?" for column in values)
    with connection:
        connection.execute(
            f"UPDATE trips SET {assignments} WHERE id = ?",
            (*values.values(), trip_id),
        )
    return get_snapshot(connection, trip_id)


def delete_trip(connection: sqlite3.Connection, trip_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT filename FROM photos WHERE trip_id = ?", (trip_id,)
    ).fetchall()
    with connection:
        cursor = connection.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    if cursor.rowcount == 0:
        raise ApiError("This trip does not exist.", status_code=404, code="trip_not_found")
    return [row["filename"] for row in rows]


def trip_exists(connection: sqlite3.Connection, trip_id: str) -> bool:
    return connection.execute("SELECT 1 FROM trips WHERE id = ?", (trip_id,)).fetchone() is not None


def photo_count(connection: sqlite3.Connection, trip_id: str) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS count FROM photos WHERE trip_id = ?", (trip_id,)
    ).fetchone()
    return int(row["count"])


def add_photo(
    connection: sqlite3.Connection,
    *,
    trip_id: str,
    filename: str,
    alt: str,
    mime: str,
    width: int,
    height: int,
    size: int,
    max_photos: int,
) -> dict[str, Any]:
    if not trip_exists(connection, trip_id):
        raise ApiError("This trip does not exist.", status_code=404, code="trip_not_found")
    count = photo_count(connection, trip_id)
    if count >= max_photos:
        raise ApiError(
            f"Each trip can hold at most {max_photos} photographs.",
            status_code=422,
            code="photo_limit_reached",
        )
    position_row = connection.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS next FROM photos WHERE trip_id = ?",
        (trip_id,),
    ).fetchone()
    photo_id = str(uuid.uuid4())
    with connection:
        connection.execute(
            """
            INSERT INTO photos
              (id, trip_id, filename, alt, mime, width, height, bytes, position, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                photo_id,
                trip_id,
                filename,
                alt,
                mime,
                width,
                height,
                size,
                int(position_row["next"]),
                now_iso(),
            ),
        )
    return {
        "id": photo_id,
        "url": f"/media/{filename}",
        "alt": alt,
        "width": width,
        "height": height,
    }


def remove_photo(connection: sqlite3.Connection, trip_id: str, photo_id: str) -> str:
    row = connection.execute(
        "SELECT filename FROM photos WHERE id = ? AND trip_id = ?", (photo_id, trip_id)
    ).fetchone()
    if row is None:
        raise ApiError("This photograph does not exist on this trip.", status_code=404, code="photo_not_found")
    with connection:
        connection.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    return row["filename"]


def remove_photo_row_by_filename(connection: sqlite3.Connection, filename: str) -> None:
    with connection:
        connection.execute("DELETE FROM photos WHERE filename = ?", (filename,))


def list_photo_filenames(connection: sqlite3.Connection, trip_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT filename FROM photos WHERE trip_id = ? ORDER BY position, created_at", (trip_id,)
    ).fetchall()
    return [row["filename"] for row in rows]


def referenced_filenames(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT filename FROM photos").fetchall()
    return {row["filename"] for row in rows}
