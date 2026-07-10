from __future__ import annotations

from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = Field(default_factory=list)
