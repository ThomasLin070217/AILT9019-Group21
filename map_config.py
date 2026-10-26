"""Dependency-free reader for the two browser-side Google Maps settings.

The preview server and the FastAPI backend share this module so both expose
exactly the same values and neither can accidentally publish another secret.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

ALLOWED_KEYS = ("GOOGLE_MAPS_API_KEY", "GOOGLE_MAPS_MAP_ID")
DEFAULT_MAP_ID = "DEMO_MAP_ID"


def _read_config_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return values
    for line in text.splitlines():
        name, separator, value = line.partition("=")
        key = name.strip()
        if separator and key in ALLOWED_KEYS:
            values[key] = value.strip().strip("\"'")
    return values


def read_map_config(root: Path | str, environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return only the browser-safe Maps settings.

    Environment values win over the local file, matching the existing preview
    server behaviour. No other environment entry is ever returned.
    """
    env = os.environ if environ is None else environ
    values = _read_config_file(Path(root) / ".env.maps.local")
    api_key = env.get("GOOGLE_MAPS_API_KEY", values.get("GOOGLE_MAPS_API_KEY", ""))
    map_id = env.get("GOOGLE_MAPS_MAP_ID", values.get("GOOGLE_MAPS_MAP_ID", DEFAULT_MAP_ID)) or DEFAULT_MAP_ID
    return {"apiKey": api_key, "mapId": map_id}
