"""Load and validate the single supported city catalogue."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from backend.errors import ApiError


@dataclass(frozen=True)
class City:
    id: str
    name: str
    local_name: str
    region: str
    longitude: float
    latitude: float
    source_ne_id: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class CityCatalogue:
    def __init__(self, cities: list[City]) -> None:
        self._cities = tuple(cities)
        self._by_id = {city.id: city for city in cities}

    def all(self) -> list[dict[str, Any]]:
        return [city.as_dict() for city in self._cities]

    def ids(self) -> set[str]:
        return set(self._by_id)

    def get(self, city_id: str) -> City | None:
        return self._by_id.get(city_id)

    def require(self, city_id: str) -> City:
        city = self.get(city_id)
        if city is None:
            raise ApiError(
                f"City {city_id!r} is not in the supported catalogue.",
                status_code=404,
                code="unknown_city",
            )
        return city

    def __len__(self) -> int:
        return len(self._cities)


def _require_text(item: Any, key: str, index: int) -> str:
    value = item.get(key) if isinstance(item, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"data/cities.json entry {index} has an invalid {key!r}.")
    return value


def load_cities(path: Path | str) -> CityCatalogue:
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"City catalogue not found at {path}.") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"City catalogue at {path} could not be read: {exc}") from exc

    if not isinstance(raw, list) or not raw:
        raise RuntimeError("data/cities.json must contain a non-empty array.")

    cities: list[City] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise RuntimeError(f"data/cities.json entry {index} is not an object.")
        city_id = _require_text(item, "id", index)
        if city_id in seen:
            raise RuntimeError(f"data/cities.json contains a duplicate city id {city_id!r}.")
        seen.add(city_id)
        longitude = item.get("longitude")
        latitude = item.get("latitude")
        if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
            raise RuntimeError(f"data/cities.json entry {city_id!r} needs numeric coordinates.")
        if not -180 <= longitude <= 180 or not -90 <= latitude <= 90:
            raise RuntimeError(f"data/cities.json entry {city_id!r} has coordinates outside the valid range.")
        source_ne_id = item.get("source_ne_id")
        if source_ne_id is not None and not isinstance(source_ne_id, int):
            raise RuntimeError(f"data/cities.json entry {city_id!r} has a non-integer source_ne_id.")
        cities.append(
            City(
                id=city_id,
                name=_require_text(item, "name", index),
                local_name=_require_text(item, "local_name", index),
                region=_require_text(item, "region", index),
                longitude=float(longitude),
                latitude=float(latitude),
                source_ne_id=source_ne_id,
            )
        )
    return CityCatalogue(cities)
