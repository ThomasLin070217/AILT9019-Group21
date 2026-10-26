"""SQLite schema and request-scoped connections."""
from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

from fastapi import Request

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
  id          TEXT PRIMARY KEY,
  city_id     TEXT NOT NULL,
  trip_date   TEXT,
  title       TEXT NOT NULL DEFAULT '',
  notes       TEXT NOT NULL DEFAULT '',
  memory_text TEXT NOT NULL DEFAULT '',
  source      TEXT NOT NULL DEFAULT 'user',
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS photos (
  id         TEXT PRIMARY KEY,
  trip_id    TEXT NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
  filename   TEXT NOT NULL UNIQUE,
  alt        TEXT NOT NULL DEFAULT '',
  mime       TEXT NOT NULL,
  width      INTEGER NOT NULL,
  height     INTEGER NOT NULL,
  bytes      INTEGER NOT NULL,
  position   INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trips_city ON trips(city_id);
CREATE INDEX IF NOT EXISTS idx_trips_date ON trips(trip_date);
CREATE INDEX IF NOT EXISTS idx_photos_trip ON photos(trip_id, position);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    """Open one connection with the PRAGMAs this single-user service needs."""
    connection = sqlite3.connect(str(path), timeout=5.0, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def init_db(path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(path)
    try:
        connection.executescript(SCHEMA)
        row = connection.execute("SELECT value FROM schema_meta WHERE key = 'version'").fetchone()
        if row is None:
            connection.execute(
                "INSERT INTO schema_meta (key, value) VALUES ('version', ?)",
                (str(SCHEMA_VERSION),),
            )
        elif int(row["value"]) != SCHEMA_VERSION:
            raise RuntimeError(
                f"Database schema version {row['value']} does not match the backend version {SCHEMA_VERSION}. "
                "Back up var/travel.db before changing it."
            )
        connection.commit()
    finally:
        connection.close()


def get_db(request: Request) -> Generator[sqlite3.Connection, None, None]:
    connection = connect(request.app.state.settings.db_path)
    try:
        yield connection
    finally:
        connection.close()
