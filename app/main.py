from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.tasks import router as tasks_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.init_db import init_db
from app.middleware.request_logging import RequestLoggingMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup", extra={"event": "startup"})
    init_db()
    yield
    logger.info("application_shutdown", extra={"event": "shutdown"})


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

app.include_router(tasks_router, prefix=f"{settings.api_prefix}/tasks", tags=["tasks"])
