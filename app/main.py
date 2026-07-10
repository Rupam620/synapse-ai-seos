from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.logging import configure_logging
import app.routes.backlog as backlog_module
import app.routes.health as health_module
import app.routes.users as users_module

health_router = health_module.router
backlog_router = backlog_module.router
users_router = users_module.router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.on_event("startup")
    def _validate_startup_settings() -> None:
        _ = get_settings()

    app.include_router(health_router)
    app.include_router(backlog_router)
    app.include_router(users_router)

    return app


app = create_app()
