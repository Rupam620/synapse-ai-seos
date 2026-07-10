from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskQueryParams, TaskResponse, TaskUpdate
from app.services.task_service import create_task, delete_task, get_task_by_id, list_tasks, update_task

router = APIRouter(prefix="/tasks")


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    task = create_task(db, payload)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks_endpoint(
    db: Session = Depends(get_db),
    status_value: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TaskResponse]:
    query = TaskQueryParams(status=status_value, priority=priority, limit=limit, offset=offset)
    tasks = list_tasks(db, query)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    task = get_task_by_id(db, task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskResponse:
    task = update_task(db, task_id, payload)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)) -> Response:
    delete_task(db, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
