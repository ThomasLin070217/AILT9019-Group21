"""Trip persistence, ordering, validation and visit invariants."""
from __future__ import annotations

import pytest


def test_health_reports_storage_and_unconfigured_ai(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "ok",
        "storage": {"database": "ok", "media": "ok"},
        "ai_configured": False,
    }
    assert "var/" not in response.text


def test_city_catalogue_matches_the_frontend_file(client):
    response = client.get("/api/cities")
    assert response.status_code == 200
    cities = response.json()
    assert len(cities) == 19
    assert len({city["id"] for city in cities}) == 19
    assert {"id", "name", "local_name", "region", "longitude", "latitude", "source_ne_id"} <= set(cities[0])


def test_create_then_list_returns_the_contract_shape(client, make_trip):
    trip = make_trip()
    assert set(trip) == {"id", "city_id", "trip_date", "title", "notes", "memory_text", "photos", "source"}
    assert trip["source"] == "user"
    assert trip["memory_text"] == ""
    assert trip["photos"] == []

    listing = client.get("/api/trips")
    assert listing.status_code == 200
    assert listing.json() == [trip]


def test_trips_survive_restart(client_factory):
    client, _ = client_factory()
    created = client.post(
        "/api/trips",
        json={"city_id": "hk-hong-kong", "trip_date": "2026-01-02", "title": "First", "notes": "Saved"},
    )
    assert created.status_code == 201

    restarted, _ = client_factory()
    listing = restarted.get("/api/trips")
    assert listing.status_code == 200
    assert [row["title"] for row in listing.json()] == ["First"]


def test_repeat_visits_are_separate_and_edits_keep_the_same_identity(client, make_trip):
    first = make_trip(city_id="jp-osaka", trip_date="2026-05-16")
    second = make_trip(city_id="jp-osaka", trip_date="2026-06-20", title="Second visit")
    assert first["id"] != second["id"]
    assert len(client.get("/api/trips").json()) == 2

    edited = client.patch(f"/api/trips/{first['id']}", json={"memory_text": "Edited memory"})
    assert edited.status_code == 200
    assert edited.json()["id"] == first["id"]
    assert edited.json()["city_id"] == first["city_id"]
    assert len(client.get("/api/trips").json()) == 2


def test_ordering_is_newest_date_first_with_unknown_dates_last(client, make_trip):
    make_trip(trip_date=None, title="Undated")
    make_trip(trip_date="2026-05-16", title="May")
    make_trip(trip_date="2026-06-20", title="June")
    titles = [trip["title"] for trip in client.get("/api/trips").json()]
    assert titles == ["June", "May", "Undated"]


@pytest.mark.parametrize(
    "payload,status",
    [
        ({"city_id": "not-a-city"}, 404),
        ({"city_id": "jp-osaka", "trip_date": "2026-02-31"}, 422),
        ({"city_id": "jp-osaka", "trip_date": "16/05/2026"}, 422),
        ({"city_id": "jp-osaka", "title": "x" * 201}, 422),
        ({"city_id": "jp-osaka", "notes": "x" * 5001}, 422),
        ({"city_id": "jp-osaka", "id": "client-chosen"}, 422),
        ({"city_id": "jp-osaka", "photos": []}, 422),
        ({"city_id": "jp-osaka", "memory_text": "not on create"}, 422),
        ({"city_id": "jp-osaka", "source": "demo"}, 422),
        ({}, 422),
    ],
)
def test_invalid_creates_write_nothing(client, payload, status):
    response = client.post("/api/trips", json=payload)
    assert response.status_code == status
    assert client.get("/api/trips").json() == []
    assert set(response.json()) == {"error"}
    assert response.json()["error"]["code"]
    assert response.json()["error"]["message"]


def test_patch_cannot_change_identity_or_city(client, make_trip):
    trip = make_trip()
    for patch in ({"id": "other"}, {"city_id": "cn-beijing"}):
        response = client.patch(f"/api/trips/{trip['id']}", json=patch)
        assert response.status_code == 422
    unchanged = client.get(f"/api/trips/{trip['id']}").json()
    assert unchanged["id"] == trip["id"]
    assert unchanged["city_id"] == trip["city_id"]


def test_patch_can_clear_the_date_and_rejects_nulls_for_text(client, make_trip):
    trip = make_trip(trip_date="2026-05-16")
    cleared = client.patch(f"/api/trips/{trip['id']}", json={"trip_date": None})
    assert cleared.status_code == 200
    assert cleared.json()["trip_date"] is None

    for body in ({"title": None}, {"notes": None}, {"memory_text": None}):
        assert client.patch(f"/api/trips/{trip['id']}", json=body).status_code == 422


def test_empty_patch_is_rejected(client, make_trip):
    trip = make_trip()
    response = client.patch(f"/api/trips/{trip['id']}", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_delete_removes_the_trip_and_returns_204(client, make_trip):
    trip = make_trip()
    response = client.delete(f"/api/trips/{trip['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/trips/{trip['id']}").status_code == 404
    assert client.get("/api/trips").json() == []
    assert client.delete(f"/api/trips/{trip['id']}").status_code == 404


def test_unknown_trip_uses_the_error_envelope(client):
    response = client.get("/api/trips/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "trip_not_found"
