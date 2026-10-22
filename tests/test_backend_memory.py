"""AI proxy confirmation, privacy boundary, timeouts and failure handling."""
from __future__ import annotations

import asyncio
import io

from PIL import Image

from backend.ai.base import MemoryResult, ProviderError, ProviderUnavailable
from conftest import jpeg_bytes, upload


class SpyGenerator:
    name = "spy"

    def __init__(self, result=None, error=None, delay: float = 0.0):
        self.result = result or MemoryResult(status="draft", title="Osaka in the rain", text="A short memory.")
        self.error = error
        self.delay = delay
        self.requests = []
        self.copies: list[list[bytes]] = []

    def is_configured(self) -> bool:
        return True

    async def generate(self, request):
        self.requests.append(request)
        # The route deletes its temporary copies after returning, so read them now.
        self.copies.append([path.read_bytes() for path in request.photo_paths])
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error:
            raise self.error
        return self.result


def test_confirmation_is_required_before_any_ai_work(client, make_trip):
    trip = make_trip()
    spy = SpyGenerator()
    client.app.state.generator = spy
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": False})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "confirmation_required"
    assert spy.requests == []


def test_missing_provider_returns_503_and_keeps_the_trip(client, make_trip):
    trip = make_trip()
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_not_configured"
    assert client.get(f"/api/trips/{trip['id']}").json() == trip


def test_only_the_selected_trip_and_sanitised_copies_are_sent(client, make_trip):
    first = make_trip(city_id="jp-osaka", title="First secret title", notes="ONLY A SECRET")
    second = make_trip(city_id="cn-beijing", title="Second secret title", notes="B SECRET")
    first_photo = upload(client, first["id"], jpeg_bytes(with_exif=True)).json()
    second_photo = upload(client, second["id"], jpeg_bytes(size=(640, 480))).json()

    spy = SpyGenerator()
    client.app.state.generator = spy
    response = client.post(f"/api/trips/{first['id']}/memory", json={"confirmed": True})
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "draft"

    assert len(spy.requests) == 1
    request = spy.requests[0]
    assert request.city_name == "Osaka"
    assert request.title == "First secret title"
    assert request.notes == "ONLY A SECRET"
    assert "B SECRET" not in f"{request.city_name}{request.title}{request.notes}"
    assert len(request.photo_paths) == 1
    assert second_photo["id"] not in response.text

    copy = Image.open(io.BytesIO(spy.copies[0][0]))
    assert copy.format == "JPEG"
    assert max(copy.size) <= 1280
    assert dict(copy.getexif()) == {}

    unchanged = client.get(f"/api/trips/{first['id']}").json()
    assert unchanged["memory_text"] == ""
    assert unchanged["photos"] == [{"id": first_photo["id"], "url": first_photo["url"], "alt": first_photo["alt"]}]


def test_clarification_result_is_returned(client, make_trip):
    trip = make_trip()
    spy = SpyGenerator(
        result=MemoryResult(
            status="clarification",
            question="Which city is in the first photograph?",
            warning="The notes do not match the photograph.",
        )
    )
    client.app.state.generator = spy
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "clarification"
    assert body["question"].startswith("Which city")


def test_timeout_returns_504_and_does_not_touch_the_trip(client_factory):
    generator = SpyGenerator(delay=0.3)
    client, _ = client_factory(generator=generator, ai_timeout_seconds=0.01)
    trip = client.post("/api/trips", json={"city_id": "jp-osaka", "title": "Keep me"}).json()
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "ai_timeout"
    assert client.get(f"/api/trips/{trip['id']}").json() == trip


def test_provider_failure_returns_502(client, make_trip):
    trip = make_trip()
    client.app.state.generator = SpyGenerator(error=ProviderError("provider exploded"))
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_provider_error"
    assert client.get(f"/api/trips/{trip['id']}").json() == trip


def test_provider_unavailable_returns_503(client, make_trip):
    trip = make_trip()
    client.app.state.generator = SpyGenerator(error=ProviderUnavailable("not configured"))
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_not_configured"


def test_empty_draft_is_malformed(client, make_trip):
    trip = make_trip()
    client.app.state.generator = SpyGenerator(result=MemoryResult(status="draft", title="", text=""))
    response = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_malformed_response"


def test_missing_trip_returns_404_before_generation(client):
    spy = SpyGenerator()
    client.app.state.generator = spy
    response = client.post("/api/trips/missing/memory", json={"confirmed": True})
    assert response.status_code == 404
    assert spy.requests == []
