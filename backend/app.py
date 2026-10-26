"""Application factory for the local Travel Memory Map backend."""
from __future__ import annotations

import logging

from fastapi import FastAPI

from backend import __version__
from backend.ai import build_generator, generator_configured
from backend.cities import load_cities
from backend.config import Settings
from backend.db import connect, init_db
from backend.errors import install_error_handlers
from backend.routers import cities, memory, photos, system, trips
from backend.security import install_security
from backend.static import install_static
from backend.storage.files import sweep_unreferenced
from backend.storage.trips import referenced_filenames

logger = logging.getLogger("travel_memory_map.backend")


def create_app(settings: Settings | None = None, generator=None) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.ensure_directories()
    init_db(settings.db_path)
    catalogue = load_cities(settings.cities_path)

    app = FastAPI(
        title="Travel Memory Map backend",
        version=__version__,
        description="Local-only trip, photo and memory service.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings = settings
    app.state.cities = catalogue
    app.state.generator = generator or build_generator(settings)

    install_error_handlers(app)
    install_security(app)

    app.include_router(system.router)
    app.include_router(cities.router)
    app.include_router(trips.router)
    app.include_router(photos.router)
    app.include_router(memory.router)
    install_static(app, settings)

    connection = connect(settings.db_path)
    try:
        referenced = referenced_filenames(connection)
    finally:
        connection.close()
    removed = sweep_unreferenced(settings.media_dir, referenced)
    if removed:
        logger.info("Removed %s unreferenced media file(s) at startup.", removed)

    logger.info(
        "Backend ready: %s cities, database %s, media %s, AI %s",
        len(catalogue),
        settings.db_path,
        settings.media_dir,
        "configured" if generator_configured(app.state.generator) else "not configured",
    )
    return app
