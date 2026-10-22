"""Select the configured AI adapter without coupling routes to a provider."""
from __future__ import annotations

import importlib
import logging

from backend.ai.base import MemoryGenerator
from backend.ai.null import NullGenerator
from backend.config import Settings

logger = logging.getLogger("travel_memory_map.backend")


def generator_configured(generator: MemoryGenerator) -> bool:
    """Never let a broken adapter take down health checks or startup."""
    try:
        return bool(generator.is_configured())
    except Exception:
        logger.exception("AI adapter %s failed its configuration check.", getattr(generator, "name", "unknown"))
        return False


def build_generator(settings: Settings) -> MemoryGenerator:
    provider = (settings.ai_provider or "null").strip().lower()
    if provider in {"", "null", "none"}:
        return NullGenerator()

    module_name = f"backend.ai.{provider}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.warning(
            "AI_PROVIDER=%s has no adapter module (%s). AI requests will return 503.",
            provider,
            module_name,
        )
        return NullGenerator()

    factory = getattr(module, "create_generator", None)
    if not callable(factory):
        logger.warning("AI adapter %s has no create_generator(settings) factory.", module_name)
        return NullGenerator()

    try:
        generator = factory(settings)
    except Exception:
        logger.exception("AI adapter %s could not be created; AI requests will return 503.", module_name)
        return NullGenerator()

    if not getattr(generator, "name", None):
        logger.warning("AI adapter %s did not declare a name; AI requests will return 503.", module_name)
        return NullGenerator()
    return generator
