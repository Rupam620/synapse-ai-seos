from __future__ import annotations

from fastapi import FastAPI

from app.config import get_settings
from app.core.logging import configure_logging
from app.routes.backlog import router as backlog_router
from app.routes.health import router as health_router
from app.routes.users import router as users_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)

    @app.on_event('startup')
    def _validate_startup_settings() -> None:
        _ = get_settings()

    app.include_router(health_router)
    app.include_router(backlog_router)
    app.include_router(users_router)

    return app


app = create_app()
