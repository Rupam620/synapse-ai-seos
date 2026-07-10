from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.enums import TaskStatus

TITLE_MAX_LEN = 200
DESCRIPTION_MAX_LEN = 2000


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=TITLE_MAX_LEN)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LEN)
    status: TaskStatus = TaskStatus.TODO
    priority: int | None = Field(default=None, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("title must not be empty")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LEN)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LEN)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("title must not be empty")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    limit: int
    offset: int
