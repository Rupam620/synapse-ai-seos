import importlib
import logging
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app_module():
    """Import app.main lazily so tests can monkeypatch around reloads if needed."""
    import app.main as main_module

    return main_module


def test_app_metadata_from_settings(app_module):
    assert app_module.app.title == app_module.settings.app_name
    assert app_module.app.version == app_module.settings.app_version


def test_tasks_router_is_included_under_configured_prefix(app_module):
    openapi = app_module.app.openapi()
    paths = openapi.get("paths", {})

    # We don't assume exact endpoint set, only that tasks routes are mounted correctly.
    assert any(path.startswith(f"{app_module.settings.api_prefix}/tasks") for path in paths.keys())


def test_request_logging_middleware_sets_request_id_header(app_module):
    with TestClient(app_module.app) as client:
        # Pick an existing endpoint from OpenAPI to avoid hardcoding assumptions.
        paths = app_module.app.openapi()["paths"]
        path = next(iter(paths.keys()))
        method = next(iter(paths[path].keys())).upper()

        response = client.request(method, path)
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"]


def test_request_logging_middleware_passthrough_request_id(app_module):
    with TestClient(app_module.app) as client:
        paths = app_module.app.openapi()["paths"]
        path = next(iter(paths.keys()))
        method = next(iter(paths[path].keys())).upper()

        request_id = "req-12345"
        response = client.request(method, path, headers={"X-Request-ID": request_id})
        assert response.headers.get("X-Request-ID") == request_id


def test_lifespan_startup_and_shutdown_logs(monkeypatch):
    import app.main as main_module

    calls = []

    class FakeLogger:
        def info(self, message, extra=None):
            calls.append((message, extra))

    monkeypatch.setattr(main_module, "logger", FakeLogger())

    async def fake_lifespan_test():
        async with main_module.lifespan(main_module.app):
            # inside app lifespan context
            pass

    import anyio

    anyio.run(fake_lifespan_test)

    assert calls[0][0] == "application_startup"
    assert calls[0][1] == {"event": "startup"}
    assert calls[-1][0] == "application_shutdown"
    assert calls[-1][1] == {"event": "shutdown"}


def test_lifespan_calls_init_db(monkeypatch):
    import app.main as main_module

    called = {"init_db": 0}

    def fake_init_db():
        called["init_db"] += 1

    monkeypatch.setattr(main_module, "init_db", fake_init_db)

    async def run_lifespan_once():
        async with main_module.lifespan(main_module.app):
            pass

    import anyio

    anyio.run(run_lifespan_once)
    assert called["init_db"] == 1


def test_global_exception_handler_produces_standard_payload_shape():
    # Build a minimal app that uses the same exception registration function
    # and request logging middleware, then assert runtime behavior.
    from app.core.handlers import register_exception_handlers
    from app.middleware.request_logging import RequestLoggingMiddleware

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("unexpected")

    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/boom", headers={"X-Request-ID": "rid-500"})

    assert resp.status_code == 500
    body = resp.json()
    assert set(body.keys()) == {"error_code", "message", "details", "request_id"}
    assert body["error_code"] == "INTERNAL_SERVER_ERROR"
    assert body["message"] == "Internal server error"
    assert body["details"] is None
    assert body["request_id"] == "rid-500"


def test_import_side_effect_configure_logging_runs(monkeypatch):
    # Validate main module calls configure_logging() on import.
    import app.main as loaded_main

    # We patch source module function then reload main to ensure call happens again.
    import app.core.logging as logging_module

    called = {"configure": 0}

    def fake_configure_logging():
        called["configure"] += 1

    monkeypatch.setattr(logging_module, "configure_logging", fake_configure_logging)

    # Reload main to trigger import-time side effects with patched function.
    import app.main as main_module
    importlib.reload(main_module)

    assert called["configure"] == 1
