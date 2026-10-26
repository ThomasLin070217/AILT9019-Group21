"""Pydantic models mirroring the shared API contract."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TITLE_LIMIT = 200
TEXT_LIMIT = 5_000
ALT_LIMIT = 200


def validate_trip_date(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("trip_date must be a YYYY-MM-DD string or null.")
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError("trip_date must use YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("trip_date must be a real calendar date.") from exc
    if parsed.isoformat() != value:
        raise ValueError("trip_date must be a real calendar date.")
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CityOut(BaseModel):
    id: str
    name: str
    local_name: str
    region: str
    longitude: float
    latitude: float
    source_ne_id: int | None = None


class PhotoPreview(BaseModel):
    id: str
    url: str
    alt: str = ""


class PhotoUploadResult(PhotoPreview):
    width: int
    height: int


class TripSnapshot(BaseModel):
    id: str
    city_id: str
    trip_date: str | None
    title: str
    notes: str
    memory_text: str
    photos: list[PhotoPreview]
    source: str


class TripCreate(StrictModel):
    city_id: str = Field(min_length=1, max_length=64)
    trip_date: str | None = None
    title: str = Field(default="", max_length=TITLE_LIMIT)
    notes: str = Field(default="", max_length=TEXT_LIMIT)

    _validate_date = field_validator("trip_date")(validate_trip_date)


class TripPatch(StrictModel):
    title: str | None = Field(default=None, max_length=TITLE_LIMIT)
    notes: str | None = Field(default=None, max_length=TEXT_LIMIT)
    memory_text: str | None = Field(default=None, max_length=TEXT_LIMIT)
    trip_date: str | None = None

    _validate_date = field_validator("trip_date")(validate_trip_date)

    @model_validator(mode="after")
    def require_change(self) -> "TripPatch":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        for name in ("title", "notes", "memory_text"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null.")
        return self


class MemoryRequestIn(StrictModel):
    """The browser must acknowledge the pre-send notice before any photo leaves."""

    confirmed: bool = False


class MemoryOut(BaseModel):
    status: Literal["draft", "clarification"]
    title: str = ""
    text: str = ""
    question: str | None = None
    warning: str | None = None
    model: str | None = None


class HealthStorage(BaseModel):
    database: Literal["ok", "unavailable"]
    media: Literal["ok", "unavailable"]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    storage: HealthStorage
    ai_configured: bool
