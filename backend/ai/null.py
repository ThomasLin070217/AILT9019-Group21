"""Honest default adapter used until a real provider is configured."""
from __future__ import annotations

from backend.ai.base import MemoryRequest, MemoryResult, ProviderUnavailable


class NullGenerator:
    name = "null"

    def is_configured(self) -> bool:
        return False

    async def generate(self, request: MemoryRequest) -> MemoryResult:
        raise ProviderUnavailable("No AI provider is configured on this local backend.")
