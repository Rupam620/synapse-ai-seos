from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    def __init__(self, db: Session) -> None:
        self.repository = TaskRepository(db)

    def create_task(self, payload: TaskCreate):
        return self.repository.create_task(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
        )

    def list_tasks(self, *, status, priority, limit: int, offset: int):
        return self.repository.list_tasks(
            status=status,
            priority=priority,
            limit=limit,
            offset=offset,
        )

    def get_task(self, task_id: int):
        task = self.repository.get_task_by_id(task_id)
        if task is None:
            raise NotFoundException(message=f"Task {task_id} not found", details={"task_id": task_id})
        return task

    def update_task(self, task_id: int, payload: TaskUpdate):
        task = self.get_task(task_id)
        updates = payload.model_dump(exclude_unset=True)

        return self.repository.update_task(
            task,
            title=updates.get("title"),
            description=updates.get("description"),
            status=updates.get("status"),
            priority=updates.get("priority"),
            apply_null_description="description" in updates and updates.get("description") is None,
            apply_null_priority="priority" in updates and updates.get("priority") is None,
        )

    def replace_task(self, task_id: int, payload: TaskCreate):
        task = self.get_task(task_id)
        return self.repository.update_task(
            task,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            apply_null_description=True,
            apply_null_priority=True,
        )

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.repository.delete_task(task)
        logger.info("task_deleted", extra={"event": "task_deleted", "task_id": task_id})
