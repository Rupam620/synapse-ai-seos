from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)


def _request_id_from_request(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    if rid:
        return rid
    return request.headers.get("X-Request-ID", "unknown")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = _request_id_from_request(request)
        status_code = 400
        if exc.error_code == "NOT_FOUND":
            status_code = 404
        elif exc.error_code == "CONFLICT":
            status_code = 409

        logger.warning(
            "application_error",
            extra={
                "event": "application_error",
                "request_id": request_id,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id_from_request(request)
        logger.exception(
            "unhandled_exception",
            extra={
                "event": "unhandled_exception",
                "request_id": request_id,
                "error_code": "INTERNAL_SERVER_ERROR",
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
                "details": None,
                "request_id": request_id,
            },
        )
