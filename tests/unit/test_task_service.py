from app.db.session import SessionLocal, init_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskQueryParams, TaskUpdate
from app.services.task_service import create_task, delete_task, get_task_by_id, list_tasks, update_task


def test_task_service_crud() -> None:
    init_db()
    db = SessionLocal()
    try:
        created = create_task(db, TaskCreate(title="Task A", status=TaskStatus.TODO, priority=2))
        fetched = get_task_by_id(db, created.id)
        assert fetched.id == created.id

        updated = update_task(db, created.id, TaskUpdate(status=TaskStatus.IN_PROGRESS))
        assert updated.status == TaskStatus.IN_PROGRESS

        listed = list_tasks(db, TaskQueryParams(limit=20, offset=0))
        assert len(listed) >= 1

        delete_task(db, created.id)
    finally:
        db.close()
