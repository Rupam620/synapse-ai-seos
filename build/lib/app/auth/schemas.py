from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: str = Field(...)
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)
    claims: dict[str, Any] = Field(default_factory=dict)
