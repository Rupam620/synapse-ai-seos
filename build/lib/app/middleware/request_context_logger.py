from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestContextLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug("request_started method=%s path=%s", request.method, request.url.path)
        response = await call_next(request)
        logger.debug("request_finished status=%s", response.status_code)
        return response
