"""Photo upload limits, metadata stripping, media serving and cascade cleanup."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from conftest import jpeg_bytes, png_bytes, upload


def test_upload_sanitises_metadata_and_serves_same_origin(client, make_trip):
    trip = make_trip()
    response = upload(client, trip["id"], jpeg_bytes(with_exif=True), alt="A castle at dusk")
    assert response.status_code == 201, response.text
    photo = response.json()
    assert photo["url"].startswith("/media/")
    assert photo["url"].endswith(".jpg")
    assert photo["alt"] == "A castle at dusk"
    assert photo["width"] == 1200 and photo["height"] == 900

    media = client.get(photo["url"])
    assert media.status_code == 200
    assert media.headers["content-type"] == "image/jpeg"
    assert media.headers["x-content-type-options"] == "nosniff"

    stored = Image.open(io.BytesIO(media.content))
    assert dict(stored.getexif()) == {}
    raw = media.content.decode("latin1")
    for private in ("TestCamera", "Test Author", "A private comment"):
        assert private not in raw

    snapshot = client.get(f"/api/trips/{trip['id']}").json()
    assert snapshot["photos"] == [{"id": photo["id"], "url": photo["url"], "alt": photo["alt"]}]


def test_png_with_alpha_is_kept_as_png(client, make_trip):
    trip = make_trip()
    response = upload(client, trip["id"], png_bytes(), filename="view.png", content_type="image/png")
    assert response.status_code == 201, response.text
    photo = response.json()
    assert photo["url"].endswith(".png")
    media = client.get(photo["url"])
    assert media.headers["content-type"] == "image/png"
    assert Image.open(io.BytesIO(media.content)).mode in {"RGBA", "LA"}


def test_oversized_upload_is_rejected_and_leaves_no_files(client_factory):
    client, settings = client_factory(max_upload_bytes=1_000)
    trip = client.post("/api/trips", json={"city_id": "jp-osaka"}).json()
    response = upload(client, trip["id"], jpeg_bytes())
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "file_too_large"
    assert list(Path(settings.media_dir).iterdir()) == []
    assert client.get(f"/api/trips/{trip['id']}").json()["photos"] == []


def test_non_image_and_animated_like_files_are_rejected(client, make_trip):
    trip = make_trip()
    response = upload(client, trip["id"], b"this is not an image", filename="fake.jpg")
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media"
    assert client.get(f"/api/trips/{trip['id']}").json()["photos"] == []


def test_tiny_image_is_rejected(client, make_trip):
    trip = make_trip()
    response = upload(client, trip["id"], jpeg_bytes(size=(32, 32)))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_image"


def test_photo_limit_is_enforced(client_factory):
    client, settings = client_factory(max_photos_per_trip=1)
    trip = client.post("/api/trips", json={"city_id": "jp-osaka"}).json()
    assert upload(client, trip["id"], jpeg_bytes()).status_code == 201
    second = upload(client, trip["id"], jpeg_bytes(size=(800, 600)))
    assert second.status_code == 422
    assert second.json()["error"]["code"] == "photo_limit_reached"
    assert len(client.get(f"/api/trips/{trip['id']}").json()["photos"]) == 1
    assert len(list(Path(settings.media_dir).glob("*.jpg"))) == 1


def test_upload_to_missing_trip_returns_404(client):
    response = upload(client, "missing-trip", jpeg_bytes())
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "trip_not_found"


def test_alt_text_is_limited(client, make_trip):
    trip = make_trip()
    response = upload(client, trip["id"], jpeg_bytes(), alt="x" * 201)
    assert response.status_code == 422
    assert client.get(f"/api/trips/{trip['id']}").json()["photos"] == []


def test_delete_photo_removes_the_row_and_file(client, make_trip):
    trip = make_trip()
    photo = upload(client, trip["id"], jpeg_bytes()).json()
    response = client.delete(f"/api/trips/{trip['id']}/photos/{photo['id']}")
    assert response.status_code == 204
    assert client.get(photo["url"]).status_code == 404
    assert client.get(f"/api/trips/{trip['id']}").json()["photos"] == []


def test_deleting_a_trip_cascades_photos_and_files(client, make_trip):
    trip = make_trip()
    photo = upload(client, trip["id"], jpeg_bytes()).json()
    path = Path(client.app.state.settings.media_dir) / Path(photo["url"]).name
    assert path.is_file()

    assert client.delete(f"/api/trips/{trip['id']}").status_code == 204
    assert not path.exists()
    assert client.get(photo["url"]).status_code == 404
    assert client.get("/api/trips").json() == []


def test_media_rejects_traversal_and_unknown_names(client):
    for path in (
        "/media/../travel.db",
        "/media/%2e%2e%2Ftravel.db",
        "/media/not-a-real-photo.jpg",
        "/media/.hidden",
        "/media/" + "a" * 36 + ".gif",
    ):
        response = client.get(path)
        assert response.status_code == 404, path
        assert response.json()["error"]["code"] == "not_found"
