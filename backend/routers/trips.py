"""Trip read and write routes."""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, Request, Response, status

from backend.db import get_db
from backend.models import TripCreate, TripPatch, TripSnapshot
from backend.storage import files
from backend.storage import trips as trip_store

router = APIRouter(tags=["trips"])


@router.get("/api/trips", response_model=list[TripSnapshot])
def list_trips(_: Request, connection: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    return trip_store.list_snapshots(connection)


@router.get("/api/trips/{trip_id}", response_model=TripSnapshot)
def read_trip(trip_id: str, connection: sqlite3.Connection = Depends(get_db)) -> dict:
    return trip_store.get_snapshot(connection, trip_id)


@router.post("/api/trips", response_model=TripSnapshot, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    request: Request,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict:
    request.app.state.cities.require(payload.city_id)
    return trip_store.create_trip(
        connection,
        city_id=payload.city_id,
        trip_date=payload.trip_date,
        title=payload.title,
        notes=payload.notes,
    )


@router.patch("/api/trips/{trip_id}", response_model=TripSnapshot)
def edit_trip(
    trip_id: str,
    payload: TripPatch,
    connection: sqlite3.Connection = Depends(get_db),
) -> dict:
    patch = payload.model_dump(exclude_unset=True)
    return trip_store.update_trip(connection, trip_id, patch)


@router.delete("/api/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: str,
    request: Request,
    connection: sqlite3.Connection = Depends(get_db),
) -> Response:
    filenames = trip_store.delete_trip(connection, trip_id)
    media_dir = request.app.state.settings.media_dir
    for filename in filenames:
        files.unlink_quiet(media_dir / filename)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
