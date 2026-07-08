from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.enums import TaskStatus
from app.db.session import get_db
from app.schemas.error import ErrorResponse
from app.schemas.task import TaskCreate, TaskListResponse, TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    service = TaskService(db)
    task = service.create_task(payload)
    return TaskRead.model_validate(task)


@router.get(
    "/",
    response_model=TaskListResponse,
)
def list_tasks(
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: int | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    service = TaskService(db)
    items, total = service.list_tasks(
        status=status_filter,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return TaskListResponse(
        items=[TaskRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse}},
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    service = TaskService(db)
    task = service.get_task(task_id)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse}},
)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskRead:
    service = TaskService(db)
    task = service.update_task(task_id, payload)
    return TaskRead.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse}},
)
def replace_task(task_id: int, payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    service = TaskService(db)
    task = service.replace_task(task_id, payload)
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> Response:
    service = TaskService(db)
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
