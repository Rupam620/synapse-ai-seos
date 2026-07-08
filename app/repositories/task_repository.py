from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.enums import TaskStatus
from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_task(
        self,
        *,
        title: str,
        description: str | None,
        status: TaskStatus,
        priority: int | None,
    ) -> Task:
        task = Task(title=title, description=description, status=status, priority=priority)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        priority: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Task], int]:
        stmt: Select[tuple[Task]] = select(Task)
        count_stmt = select(func.count(Task.id))

        if status is not None:
            stmt = stmt.where(Task.status == status)
            count_stmt = count_stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
            count_stmt = count_stmt.where(Task.priority == priority)

        stmt = stmt.order_by(Task.id.asc()).offset(offset).limit(limit)

        items = list(self.db.scalars(stmt).all())
        total = self.db.scalar(count_stmt) or 0
        return items, int(total)

    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def update_task(
        self,
        task: Task,
        *,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        priority: int | None = None,
        apply_null_description: bool = False,
        apply_null_priority: bool = False,
    ) -> Task:
        if title is not None:
            task.title = title
        if description is not None or apply_null_description:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None or apply_null_priority:
            task.priority = priority

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
