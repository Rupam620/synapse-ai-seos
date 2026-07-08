from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import app.main as main_module
from app.middleware.request_context_logger import RequestContextLoggingMiddleware


@contextmanager
def lifespan_client() -> Generator[TestClient, None, None]:
    """Ensure FastAPI lifespan events run for startup assertions."""
    with TestClient(main_module.app) as client:
        yield client


def test_health_endpoint_contract() -> None:
    with lifespan_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_response_includes_request_id_header_from_middleware() -> None:
    with lifespan_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_lifespan_startup_invokes_logging_and_db_init(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, Any] = {
        "configure_logging": None,
        "get_logger_name": None,
        "logger_info": None,
        "init_db_called": 0,
    }

    class DummyLogger:
        def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
            calls["logger_info"] = {"message": message, "extra": extra}

    def fake_configure_logging(level: str) -> None:
        calls["configure_logging"] = level

    def fake_get_logger(name: str) -> DummyLogger:
        calls["get_logger_name"] = name
        return DummyLogger()

    def fake_init_db() -> None:
        calls["init_db_called"] += 1

    monkeypatch.setattr(main_module, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(main_module, "get_logger", fake_get_logger)
    monkeypatch.setattr(main_module, "init_db", fake_init_db)

    with lifespan_client() as client:
        # trigger any request to ensure app is fully running
        response = client.get("/health")
        assert response.status_code == 200

    assert calls["configure_logging"] == main_module.settings.LOG_LEVEL
    assert calls["get_logger_name"] == main_module.__name__
    assert calls["init_db_called"] == 1

    log_call = calls["logger_info"]
    assert log_call is not None
    assert log_call["message"] == "service_start"
    assert isinstance(log_call["extra"], dict)
    assert log_call["extra"]["event"] == "service_start"
    assert log_call["extra"]["app_name"] == main_module.settings.APP_NAME
    assert log_call["extra"]["environment"] == main_module.settings.ENVIRONMENT


def test_app_has_request_context_logging_middleware_registered() -> None:
    middleware_classes = [m.cls for m in main_module.app.user_middleware]
    assert RequestContextLoggingMiddleware in middleware_classes


def test_tasks_router_is_mounted_under_api_v1_prefix() -> None:
    routes = [r for r in main_module.app.routes if isinstance(r, APIRoute)]
    route_paths = {r.path for r in routes}

    # This app includes router from app.api.v1.tasks with prefix /api/v1
    # We assert at least one tasks route exists under expected namespace.
    assert any(path.startswith("/api/v1/tasks") for path in route_paths), route_paths


def test_openapi_exposes_health_and_tasks_paths() -> None:
    with lifespan_client() as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/health" in schema["paths"]
    assert any(path.startswith("/api/v1/tasks") for path in schema["paths"].keys())
