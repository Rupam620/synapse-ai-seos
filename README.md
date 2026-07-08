# Synapse AI-SEOS

A modular FastAPI REST API for backlog task management with:
- Layered architecture (API → service → repository → DB)
- Pydantic v2 request/response validation
- Structured request logging middleware with request correlation ID
- SQLite in-memory database (shared in-process lifecycle)

## Tech Stack
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- SQLite in-memory
- Pytest, Ruff, Black, Mypy

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Open docs:
- http://localhost:8000/docs
- http://localhost:8000/openapi.json

## Test & Quality
```bash
pytest -q
ruff check .
black --check .
mypy app
```

## API Overview
Base path: `/api/v1/tasks`
- `POST /` create task
- `GET /` list tasks with optional filters/pagination
- `GET /{task_id}` get task
- `PATCH /{task_id}` partial update
- `PUT /{task_id}` full mutable update
- `DELETE /{task_id}` delete task

## In-memory DB Behavior
The app uses shared in-memory SQLite via SQLAlchemy `StaticPool`. Data persists only while the process is running and resets on restart by design.

## Design Decisions
- **Task ID**: integer primary key
- **Priority**: bounded integer `1..5`
- **Status**: enum `todo | in_progress | done`
- **Update semantics**: both PATCH and PUT supported
