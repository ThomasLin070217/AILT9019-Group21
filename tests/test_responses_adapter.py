"""Chat Completions adapter tests using a fake HTTP transport only."""
from __future__ import annotations

import asyncio
import base64
import json

import httpx
import pytest

from backend.ai.base import MemoryRequest, ProviderError
from backend.ai.responses import ResponsesGenerator
from backend.config import Settings
from conftest import jpeg_bytes, upload


def run(coroutine):
    return asyncio.run(coroutine)


def generator(tmp_path, handler, *, base_url="https://api.openai.com/v1", model="test-model"):
    settings = Settings(
        root=tmp_path,
        ai_api_key="test-only-key",
        ai_model=model,
        ai_base_url=base_url,
        ai_timeout_seconds=2,
    )
    return ResponsesGenerator(settings, httpx.MockTransport(handler))


def request(tmp_path):
    photo = tmp_path / "current.jpg"
    photo.write_bytes(b"sanitised-photo")
    return MemoryRequest(
        city_name="Hangzhou",
        trip_date=None,
        title="",
        notes="An afternoon visit",
        photo_paths=(photo,),
    )


def completion(result, model="test-model"):
    return {"model": model, "choices": [{"message": {"content": json.dumps(result)}}]}


def valid_draft():
    return {
        "status": "draft",
        "title": "Hangzhou afternoon",
        "memory_text": "I spent an afternoon in Hangzhou.",
        "warnings": [],
        "questions": [],
    }


def test_payload_is_single_trip_and_draft_is_not_saved(tmp_path):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=completion(valid_draft()))

    result = run(generator(tmp_path, handler).generate(request(tmp_path)))
    assert result.status == "draft" and result.model == "test-model"
    assert str(seen[0].url) == "https://api.openai.com/v1/chat/completions"
    payload = json.loads(seen[0].content)
    assert payload["messages"][0]["role"] == "system"
    content = payload["messages"][1]["content"]
    assert "Hangzhou" in content[0]["text"]
    image = content[1]["image_url"]["url"]
    assert base64.b64decode(image.split(",", 1)[1]) == b"sanitised-photo"


def test_course_gateway_uses_chat_completions_and_fenced_json(tmp_path):
    seen = []

    def handler(req):
        seen.append(req)
        body = valid_draft()
        return httpx.Response(200, json={"choices": [{"message": {"content": "```json\n" + json.dumps(body) + "\n```"}}]})

    adapter = generator(
        tmp_path,
        handler,
        base_url="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        model="qwen3.8-flash",
    )
    result = run(adapter.generate(request(tmp_path)))
    assert result.status == "draft"
    assert str(seen[0].url).endswith("/compatible-mode/v1/chat/completions")
    payload = json.loads(seen[0].content)
    assert payload["max_tokens"] == 600
    assert payload["messages"][1]["role"] == "user"


def test_invalid_model_output_and_redirect_are_rejected(tmp_path):
    def bad_output(req):
        return httpx.Response(200, json=completion({"status": "draft", "title": "Invented", "memory_text": "X"}))

    with pytest.raises(ProviderError):
        run(generator(tmp_path, bad_output).generate(request(tmp_path)))

    def redirect(req):
        return httpx.Response(307, headers={"Location": "https://example.net/steal"})

    with pytest.raises(ProviderError):
        run(generator(tmp_path, redirect).generate(request(tmp_path)))


def test_unsafe_request_can_return_refusal_without_a_draft(tmp_path):
    def refusal(req):
        return httpx.Response(200, json=completion({"status": "refusal", "title": "",
            "memory_text": "", "warnings": ["I cannot identify people or reveal private data."],
            "questions": []}))
    result = run(generator(tmp_path, refusal).generate(request(tmp_path)))
    assert result.status == "refusal"
    assert result.title == result.text == ""
    assert "private data" in result.warning

    def unsafe_draft(req):
        return httpx.Response(200, json=completion({"status": "refusal", "title": "Leaked",
            "memory_text": "private text", "warnings": ["Declined"], "questions": []}))
    with pytest.raises(ProviderError):
        run(generator(tmp_path, unsafe_draft).generate(request(tmp_path)))


def test_existing_local_ai_config_is_recognised(tmp_path):
    (tmp_path / ".env.ai.local").write_text(
        "TRAVEL_AI_API_KEY=test\nTRAVEL_AI_MODEL=qwen3.8-flash\n"
        "TRAVEL_AI_BASE_URL=https://api.openai.com/v1\n"
    )
    settings = Settings.from_env(tmp_path, environ={})
    assert settings.ai_provider == "responses"
    assert settings.ai_api_key == "test"
    assert settings.ai_model == "qwen3.8-flash"


def test_combined_route_returns_editable_draft_without_changing_saved_trip(tmp_path, client_factory):
    seen = []

    def handler(req):
        seen.append(json.loads(req.content))
        return httpx.Response(200, json=completion(valid_draft()))

    adapter = generator(tmp_path, handler)
    client, _ = client_factory(generator=adapter)
    trip = client.post("/api/trips", json={"city_id": "cn-hangzhou", "notes": "An afternoon visit"}).json()
    upload(client, trip["id"], jpeg_bytes())
    before = client.get(f"/api/trips/{trip['id']}").json()
    result = client.post(f"/api/trips/{trip['id']}/memory", json={"confirmed": True})
    assert result.status_code == 200, result.text
    assert result.json()["text"] == "I spent an afternoon in Hangzhou."
    assert client.get(f"/api/trips/{trip['id']}").json() == before
    assert len(seen) == 1
    assert "Hangzhou" in seen[0]["messages"][1]["content"][0]["text"]
