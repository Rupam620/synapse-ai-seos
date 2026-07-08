import importlib
import logging
import sys
from types import SimpleNamespace

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


@pytest.fixture
def main_module(monkeypatch):
    """
    Import app.main with all external dependencies patched so tests are isolated,
    deterministic, and do not require real DB/config/logging internals.
    """
    # Ensure a clean import each time so module-level side effects are controlled.
    sys.modules.pop("app.main", None)

    # Patch settings object expected by app.main
    import app.core.config as config_module

    fake_settings = SimpleNamespace(
        app_name="Test Service",
        app_version="9.9.9",
        app_env="test",
        cors_allow_origins=["https://example.com"],
    )
    monkeypatch.setattr(config_module, "settings", fake_settings, raising=True)

    # Patch logging setup/get_logger used at import time
    import app.core.logging_config as logging_config_module

    setup_logging_called = {"count": 0}

    def fake_setup_logging():
        setup_logging_called["count"] += 1

    logger = logging.getLogger("test-main-logger")
    logger.setLevel(logging.INFO)

    monkeypatch.setattr(logging_config_module, "setup_logging", fake_setup_logging, raising=True)
    monkeypatch.setattr(logging_config_module, "get_logger", lambda _: logger, raising=True)

    # Patch DB init used in lifespan startup
    import app.db.session as db_session_module

    init_db_called = {"count": 0}

    def fake_init_db():
        init_db_called["count"] += 1

    monkeypatch.setattr(db_session_module, "init_db", fake_init_db, raising=True)

    # Patch API router included by module
    import app.api.v1.router as api_router_module

    router = APIRouter()

    @router.get("/v1/ping", tags=["v1"])
    def ping():
        return {"pong": True}

    monkeypatch.setattr(api_router_module, "api_v1_router", router, raising=True)

    # Import module under test after patches are in place
    mod = importlib.import_module("app.main")

    # expose helper counters for assertions
    mod._test_setup_logging_called = setup_logging_called
    mod._test_init_db_called = init_db_called
    return mod


def _has_middleware(app: FastAPI, middleware_cls: type) -> bool:
    return any(m.cls is middleware_cls for m in app.user_middleware)


def test_app_metadata_and_middlewares(main_module):
    app = main_module.app

    assert app.title == "Test Service"
    assert app.version == "9.9.9"

    # Custom request logging middleware should be installed
    from app.middleware.logging import RequestLoggingMiddleware

    assert _has_middleware(app, RequestLoggingMiddleware)

    # CORS middleware should be installed when cors_allow_origins is non-empty
    assert _has_middleware(app, CORSMiddleware)


def test_setup_logging_called_once_on_import(main_module):
    assert main_module._test_setup_logging_called["count"] == 1


def test_health_endpoint(main_module):
    with TestClient(main_module.app) as client:
        res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_included_v1_router_endpoint(main_module):
    with TestClient(main_module.app) as client:
        res = client.get("/v1/ping")

    assert res.status_code == 200
    assert res.json() == {"pong": True}


def test_lifespan_startup_calls_init_db_and_logs(main_module, monkeypatch):
    logs = []

    def fake_info(message, *args, **kwargs):
        logs.append((message, kwargs.get("extra")))

    monkeypatch.setattr(main_module.logger, "info", fake_info, raising=True)

    with TestClient(main_module.app):
        # entering context triggers startup
        pass

    assert main_module._test_init_db_called["count"] == 1

    startup = [entry for entry in logs if entry[0] == "application_startup"]
    assert len(startup) == 1
    assert startup[0][1] == {"db_mode": "sqlite_in_memory", "app_env": "test"}

    shutdown = [entry for entry in logs if entry[0] == "application_shutdown"]
    assert len(shutdown) == 1


def test_global_exception_handler_returns_500_and_logs(main_module, monkeypatch):
    # Attach a route that raises generic exception to trigger global handler
    @main_module.app.get("/boom")
    def boom():
        raise RuntimeError("kaboom")

    exception_calls = []

    def fake_exception(message, *args, **kwargs):
        exception_calls.append((message, kwargs.get("extra")))

    monkeypatch.setattr(main_module.logger, "exception", fake_exception, raising=True)

    # Prevent TestClient from re-raising server exceptions so we can assert response
    with TestClient(main_module.app, raise_server_exceptions=False) as client:
        res = client.get("/boom")

    assert res.status_code == 500
    assert res.json() == {"detail": "Internal Server Error"}

    assert len(exception_calls) == 1
    msg, extra = exception_calls[0]
    assert msg == "unhandled_exception"
    assert extra["path"] == "/boom"
    assert extra["method"] == "GET"
    assert "kaboom" in extra["error"]


def test_cors_preflight_headers_present(main_module):
    with TestClient(main_module.app) as client:
        res = client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

    # Starlette CORS middleware responds to preflight requests directly
    assert res.status_code in (200, 204)
    assert res.headers.get("access-control-allow-origin") == "https://example.com"
    allow_methods = res.headers.get("access-control-allow-methods", "")
    for method in ["GET", "POST", "PATCH", "DELETE"]:
        assert method in allow_methods


def test_global_exception_handler_direct_call(main_module):
    # Unit-level direct invocation of handler function for deterministic coverage.
    class DummyURL:
        path = "/unit-error"

    req = SimpleNamespace(url=DummyURL(), method="POST")

    async def run():
        return await main_module.global_exception_handler(req, ValueError("bad"))

    import asyncio

    response = asyncio.run(run())
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body == b'{"detail":"Internal Server Error"}'
