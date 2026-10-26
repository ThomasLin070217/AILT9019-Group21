"""City catalogue route."""
from __future__ import annotations

from fastapi import APIRouter, Request

from backend.models import CityOut

router = APIRouter(tags=["cities"])


@router.get("/api/cities", response_model=list[CityOut])
def list_cities(request: Request) -> list[dict]:
    return request.app.state.cities.all()
