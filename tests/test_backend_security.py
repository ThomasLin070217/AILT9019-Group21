"""Error envelopes, dotfile blocking and local-only Maps configuration."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.ai.null import NullGenerator
from backend.app import create_app
from conftest import build_settings


def test_unknown_route_uses_the_error_envelope(client):
    response = client.get("/api/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_method_not_allowed_uses_the_error_envelope(client):
    response = client.delete("/api/trips")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_dotfiles_are_never_served(client):
    for path in ("/data/.hidden", "/data/.env.maps.local", "/app/.gitignore"):
        response = client.get(path)
        assert response.status_code == 404, path
        assert response.json()["error"]["code"] == "not_found"


def test_security_headers_are_present_on_the_app(client):
    response = client.get("/app/")
    assert response.status_code == 200
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_validation_errors_do_not_echo_private_notes(client, make_trip):
    trip = make_trip(notes="A PRIVATE NOTE THAT MUST NOT LEAK")
    response = client.patch(f"/api/trips/{trip['id']}", json={"title": "x" * 201})
    assert response.status_code == 422
    assert "PRIVATE NOTE" not in response.text


def test_health_never_exposes_paths_or_keys(client):
    body = client.get("/api/health").text
    assert "/Users/" not in body
    assert "api_key" not in body.lower()
    assert "var/" not in body


def test_map_config_is_forbidden_from_a_non_local_host(client):
    response = client.get("/api/map-config")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_origin"


def test_map_config_is_available_on_the_local_preview_origin(tmp_path):
    settings = build_settings(tmp_path, port=8019)
    app = create_app(settings=settings, generator=NullGenerator())
    with TestClient(app, base_url="http://127.0.0.1:8019") as local:
        response = local.get("/api/map-config")
        assert response.status_code == 200
        assert set(response.json()) == {"apiKey", "mapId"}

        cross_origin = local.get("/api/map-config", headers={"Origin": "https://evil.example"})
        assert cross_origin.status_code == 403


def test_root_redirects_to_the_app(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/app/"


def test_media_directory_is_not_mounted(client, tmp_path):
    # Even a correctly named file under var/ must not be reachable by path.
    settings = client.app.state.settings
    stray = Path(settings.media_dir) / ("a" * 36 + ".jpg")
    stray.write_bytes(b"not an image")
    response = client.get(f"/media/{stray.name}")
    assert response.status_code == 404
