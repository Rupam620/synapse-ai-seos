import pytest
from pydantic import ValidationError

from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def test_task_create_trims_title() -> None:
    payload = TaskCreate(title="  hello  ", priority=3)
    assert payload.title == "hello"


def test_task_create_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title="   ")


def test_task_create_priority_bounds() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title="ok", priority=0)


def test_task_update_requires_one_field() -> None:
    with pytest.raises(ValidationError):
        TaskUpdate()


def test_task_update_accepts_status() -> None:
    payload = TaskUpdate(status=TaskStatus.DONE)
    assert payload.status == TaskStatus.DONE
