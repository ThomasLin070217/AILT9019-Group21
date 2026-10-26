"""Runtime settings for the local Travel Memory Map backend.

Everything has a safe local default. Tests construct ``Settings`` directly with
temporary paths so they never touch a developer's real album.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]

MIB = 1024 * 1024


def _load_env_file(path: Path, environ: dict[str, str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        name, separator, value = stripped.partition("=")
        name = name.strip()
        if not separator or not name or name in environ:
            continue
        environ[name] = value.strip().strip("\"'")


def load_dotenv(root: Path | str = REPO_ROOT, environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Load ``.env`` and ``.env.maps.local`` without overriding real env vars."""
    target = dict(os.environ) if environ is None else dict(environ)
    for name in (".env", ".env.maps.local"):
        _load_env_file(Path(root) / name, target)
    return target


def _inside(path: Path, root: Path) -> Path:
    path = Path(path)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


@dataclass(frozen=True)
class Settings:
    root: Path = REPO_ROOT
    app_dir: Path | None = None
    data_dir: Path | None = None
    cities_path: Path | None = None
    db_path: Path | None = None
    media_dir: Path | None = None
    tmp_dir: Path | None = None

    host: str = "127.0.0.1"
    port: int = 8019

    max_photos_per_trip: int = 8
    max_upload_bytes: int = 10 * MIB
    min_image_edge: int = 64
    max_image_pixels: int = 40_000_000
    stored_max_edge: int = 2400
    stored_jpeg_quality: int = 85
    ai_max_edge: int = 1280
    ai_jpeg_quality: int = 80

    ai_provider: str = ""
    ai_api_key: str = ""
    ai_model: str = ""
    ai_base_url: str = ""
    ai_timeout_seconds: float = 20.0

    def __post_init__(self) -> None:
        root = Path(self.root).expanduser().resolve()
        object.__setattr__(self, "root", root)
        defaults = {
            "app_dir": root / "app",
            "data_dir": root / "data",
            "cities_path": root / "data" / "cities.json",
            "db_path": root / "var" / "travel.db",
            "media_dir": root / "var" / "media",
            "tmp_dir": root / "var" / "tmp",
        }
        for name, default in defaults.items():
            value = getattr(self, name)
            object.__setattr__(self, name, default if value is None else _inside(Path(value), root))

    def ensure_directories(self) -> None:
        for folder in (self.db_path.parent, self.media_dir, self.tmp_dir):
            folder.mkdir(parents=True, exist_ok=True)
            try:
                folder.chmod(0o700)
            except OSError:
                # Best effort on platforms that do not support POSIX modes.
                pass

    @classmethod
    def from_env(cls, root: Path | str = REPO_ROOT, environ: Mapping[str, str] | None = None) -> "Settings":
        env = load_dotenv(root, environ)

        def integer(name: str, default: int) -> int:
            raw = env.get(name, "").strip()
            if not raw:
                return default
            try:
                return int(raw)
            except ValueError as exc:
                raise ValueError(f"{name} must be an integer, got {raw!r}") from exc

        def number(name: str, default: float) -> float:
            raw = env.get(name, "").strip()
            if not raw:
                return default
            try:
                return float(raw)
            except ValueError as exc:
                raise ValueError(f"{name} must be a number, got {raw!r}") from exc

        return cls(
            root=root,
            db_path=env.get("TMM_DB_PATH") or None,
            media_dir=env.get("TMM_MEDIA_DIR") or None,
            tmp_dir=env.get("TMM_TMP_DIR") or None,
            host=env.get("HOST", "127.0.0.1") or "127.0.0.1",
            port=integer("PORT", 8019),
            max_photos_per_trip=integer("TMM_MAX_PHOTOS", 8),
            max_upload_bytes=integer("TMM_MAX_UPLOAD_BYTES", 10 * MIB),
            min_image_edge=integer("TMM_MIN_IMAGE_EDGE", 64),
            max_image_pixels=integer("TMM_MAX_IMAGE_PIXELS", 40_000_000),
            stored_max_edge=integer("TMM_STORED_MAX_EDGE", 2400),
            stored_jpeg_quality=integer("TMM_STORED_JPEG_QUALITY", 85),
            ai_max_edge=integer("TMM_AI_MAX_EDGE", 1280),
            ai_jpeg_quality=integer("TMM_AI_JPEG_QUALITY", 80),
            ai_provider=env.get("AI_PROVIDER", "").strip(),
            ai_api_key=env.get("AI_API_KEY", "").strip(),
            ai_model=env.get("AI_MODEL", "").strip(),
            ai_base_url=env.get("AI_BASE_URL", "").strip(),
            ai_timeout_seconds=number("AI_TIMEOUT_SECONDS", 20.0),
        )


def connect_allowed_hosts(settings: Settings) -> set[str]:
    """Hosts permitted to read the browser Maps configuration."""
    return {
        f"127.0.0.1:{settings.port}",
        f"localhost:{settings.port}",
        f"[::1]:{settings.port}",
    }
