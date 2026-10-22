"""Provider-neutral AI boundary.

Qingyang implements one adapter module against ``MemoryGenerator``. Owen's
routes never import a provider SDK and never pass credentials into prompts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, Field


class ProviderUnavailable(Exception):
    """No provider is configured; the route returns 503."""


class ProviderError(Exception):
    """The provider failed or returned unusable output; the route returns 502."""


@dataclass(frozen=True)
class MemoryRequest:
    """Only the selected trip is ever placed in this object."""

    city_name: str
    trip_date: str | None
    title: str
    notes: str
    photo_paths: tuple[Path, ...]


class MemoryResult(BaseModel):
    status: Literal["draft", "clarification"]
    title: str = Field(default="", max_length=200)
    text: str = Field(default="", max_length=5_000)
    question: str | None = Field(default=None, max_length=500)
    warning: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=100)


class MemoryGenerator(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    async def generate(self, request: MemoryRequest) -> MemoryResult:
        ...
