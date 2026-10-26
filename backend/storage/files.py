"""Safe, atomic handling of files on disk."""
from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path

from backend.errors import NotFoundError

logger = logging.getLogger("travel_memory_map.backend")

MEDIA_NAME = re.compile(r"^[0-9a-f-]{36}\.(?:jpg|png)$")


def require_media_name(filename: str) -> str:
    if not MEDIA_NAME.fullmatch(filename):
        raise NotFoundError("Media file not found.")
    return filename


def media_path(media_dir: Path, filename: str) -> Path:
    """Resolve a stored media file without allowing traversal."""
    require_media_name(filename)
    root = Path(media_dir).resolve()
    path = (root / filename).resolve()
    if path.parent != root:
        raise NotFoundError("Media file not found.")
    return path


def atomic_install(temporary: Path, destination: Path) -> None:
    """Move a fully written file into place in one filesystem operation."""
    temporary = Path(temporary)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temporary, destination)


def unlink_quiet(path: Path | None) -> None:
    if path is None:
        return
    try:
        Path(path).unlink()
    except FileNotFoundError:
        return
    except OSError as exc:
        logger.warning("Could not remove %s: %s", Path(path).name, exc)


def sweep_unreferenced(media_dir: Path, referenced: set[str], max_age_seconds: int = 3600) -> int:
    """Remove old files with no database row; never touch a fresh upload."""
    root = Path(media_dir)
    if not root.is_dir():
        return 0
    cutoff = time.time() - max_age_seconds
    removed = 0
    for entry in root.iterdir():
        if not entry.is_file() or not MEDIA_NAME.fullmatch(entry.name):
            continue
        if entry.name in referenced:
            continue
        try:
            if entry.stat().st_mtime > cutoff:
                continue
            entry.unlink()
            removed += 1
        except OSError as exc:
            logger.warning("Could not sweep %s: %s", entry.name, exc)
    return removed
