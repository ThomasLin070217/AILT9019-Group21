"""Shared pytest fixtures for the local backend."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ai.null import NullGenerator  # noqa: E402
from backend.app import create_app  # noqa: E402
from backend.config import Settings  # noqa: E402


def build_settings(tmp_path: Path, **overrides) -> Settings:
    values = {
        "root": ROOT,
        "db_path": tmp_path / "travel.db",
        "media_dir": tmp_path / "media",
        "tmp_dir": tmp_path / "tmp",
    }
    values.update(overrides)
    return Settings(**values)


def jpeg_bytes(size: tuple[int, int] = (1200, 900), with_exif: bool = False) -> bytes:
    image = Image.new("RGB", size, (120, 90, 60))
    options: dict = {}
    if with_exif:
        exif = Image.Exif()
        exif[0x010F] = "TestCamera"
        exif[0x013B] = "Test Author"
        exif[0x9286] = "A private comment"
        try:
            exif[0x8825] = {1: "N", 2: (35, 0, 0), 3: "E", 4: (135, 0, 0)}
        except Exception:
            pass
        options["exif"] = exif
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", **options)
    return buffer.getvalue()


def png_bytes(size: tuple[int, int] = (200, 150), alpha: bool = True) -> bytes:
    mode = "RGBA" if alpha else "RGB"
    image = Image.new(mode, size, (10, 120, 90, 180) if alpha else (10, 120, 90))
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def upload(client: TestClient, trip_id: str, data: bytes, *, filename: str = "photo.jpg", content_type: str = "image/jpeg", alt: str = ""):
    return client.post(
        f"/api/trips/{trip_id}/photos",
        files={"file": (filename, data, content_type)},
        data={"alt": alt},
    )


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return build_settings(tmp_path)


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings=settings, generator=NullGenerator()))


@pytest.fixture
def client_factory(tmp_path: Path):
    created: list[TestClient] = []

    def build(generator=None, **overrides):
        settings = build_settings(tmp_path, **overrides)
        app = create_app(settings=settings, generator=generator or NullGenerator())
        test_client = TestClient(app)
        created.append(test_client)
        return test_client, settings

    yield build
    for test_client in created:
        test_client.close()


@pytest.fixture
def make_trip(client: TestClient):
    def create(**payload):
        body = {
            "city_id": "jp-osaka",
            "trip_date": "2026-05-16",
            "title": "A rainy weekend",
            "notes": "Fictional notes for testing.",
        }
        body.update(payload)
        response = client.post("/api/trips", json=body)
        assert response.status_code == 201, response.text
        return response.json()

    return create
