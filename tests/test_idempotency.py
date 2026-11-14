"""Retry identity must not collapse intentional return visits or resurrect deletions."""
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.db import connect, init_db
from conftest import jpeg_bytes, upload

BODY = {"city_id": "jp-osaka", "title": "Return visit", "notes": "Synthetic test"}
HEADERS = {"Idempotency-Key": "retry-test-0001"}


def test_same_key_replays_current_trip_after_edit_and_restart(client_factory):
    client, _ = client_factory()
    first = client.post("/api/trips", json=BODY, headers=HEADERS)
    assert first.status_code == 201
    tid = first.json()["id"]
    edited = client.patch(f"/api/trips/{tid}", json={"memory_text": "Keep my edit"}).json()
    restarted, _ = client_factory()
    retry = restarted.post("/api/trips", json=BODY, headers=HEADERS)
    assert retry.status_code == 201
    assert retry.json() == edited
    assert len(restarted.get("/api/trips").json()) == 1


def test_payload_conflict_and_deleted_trip_are_not_recreated(client):
    first = client.post("/api/trips", json=BODY, headers=HEADERS).json()
    conflict = client.post("/api/trips", json={**BODY, "notes": "Different"}, headers=HEADERS)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"
    assert len(client.get("/api/trips").json()) == 1
    client.delete(f"/api/trips/{first['id']}")
    assert client.post("/api/trips", json=BODY, headers=HEADERS).status_code == 410
    assert client.get("/api/trips").json() == []


def test_new_keys_and_legacy_unkeyed_calls_allow_identical_return_visits(client):
    responses = [client.post("/api/trips", json=BODY, headers={"Idempotency-Key": key}) for key in ["visit-one", "visit-two"]]
    responses += [client.post("/api/trips", json=BODY) for _ in range(2)]
    assert all(r.status_code == 201 for r in responses)
    assert len({r.json()["id"] for r in responses}) == 4


@pytest.mark.parametrize("key", ["short", "x" * 129, "invalid key"])
def test_invalid_key_writes_nothing(client, key):
    assert client.post("/api/trips", json=BODY, headers={"Idempotency-Key": key}).status_code == 422
    assert client.get("/api/trips").json() == []


def test_concurrent_same_key_requests_create_exactly_one_trip(client):
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: client.post("/api/trips", json=BODY, headers=HEADERS), range(8)))
    assert all(r.status_code == 201 for r in responses)
    assert len({r.json()["id"] for r in responses}) == 1
    assert len(client.get("/api/trips").json()) == 1


def test_version_one_migration_preserves_trip_photo_and_is_repeatable(client_factory):
    client, settings = client_factory()
    original = client.post("/api/trips", json=BODY).json()
    assert upload(client, original["id"], jpeg_bytes()).status_code == 201
    before = client.get("/api/trips").json()
    with connect(settings.db_path) as db:
        db.execute("DROP TABLE trip_create_requests")
        db.execute("UPDATE schema_meta SET value='1' WHERE key='version'")
    init_db(settings.db_path)
    init_db(settings.db_path)
    restarted, _ = client_factory()
    assert restarted.get("/api/trips").json() == before
    assert restarted.get(before[0]["photos"][0]["url"]).status_code == 200
    assert restarted.post("/api/trips", json=BODY, headers=HEADERS).status_code == 201


def test_unsupported_schema_is_not_modified(tmp_path):
    path = tmp_path / "future.db"
    with connect(path) as db:
        db.execute("CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT)")
        db.execute("INSERT INTO schema_meta VALUES ('version', '999')")
    with pytest.raises(RuntimeError, match="Unsupported"):
        init_db(path)
    with connect(path) as db:
        assert db.execute("SELECT name FROM sqlite_master WHERE name='trips'").fetchone() is None
