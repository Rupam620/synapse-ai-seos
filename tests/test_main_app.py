from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import app.main as main_module


def _iter_route_like(route_obj: object) -> Iterable[object]:
    path = getattr(route_obj, "path", None)
    if isinstance(path, str):
        yield route_obj

    original_router = getattr(route_obj, "original_router", None)
    if original_router is not None:
        for nested in getattr(original_router, "routes", []):
            yield from _iter_route_like(nested)


def _extract_registered_paths(app: FastAPI) -> set[str]:
    paths: set[str] = set()
    for route in app.router.routes:
        for concrete in _iter_route_like(route):
            p = getattr(concrete, "path", None)
            if isinstance(p, str):
                paths.add(p)
    return paths


def test_create_app_uses_settings_for_title_and_configures_logging(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, object] = {"log_level": None, "settings_calls": 0}

    fake_settings = SimpleNamespace(app_name="Synapse Test API", log_level="DEBUG")

    def fake_get_settings():
        calls["settings_calls"] = int(calls["settings_calls"]) + 1
        return fake_settings

    def fake_configure_logging(level: str):
        calls["log_level"] = level

    monkeypatch.setattr(main_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(main_module, "configure_logging", fake_configure_logging)

    app = main_module.create_app()

    assert app.title == "Synapse Test API"
    assert calls["log_level"] == "DEBUG"
    assert calls["settings_calls"] >= 1


def test_create_app_registers_health_backlog_users_routers_by_paths():
    app = main_module.create_app()
    paths = _extract_registered_paths(app)

    assert "/health" in paths
    assert "/backlog" in paths
    assert "/users/me" in paths


def test_http_exception_handler_returns_standardized_json_and_headers():
    app = main_module.create_app()

    @app.get("/__test_http_exception")
    def _raise_http_exc():
        raise HTTPException(
            status_code=418,
            detail={"code": "teapot", "message": "short and stout"},
            headers={"X-Test-Header": "present"},
        )

    with TestClient(app) as client:
        response = client.get("/__test_http_exception")

    assert response.status_code == 418
    assert response.json() == {"detail": {"code": "teapot", "message": "short and stout"}}
    assert response.headers.get("x-test-header") == "present"


def test_startup_event_revalidates_settings(monkeypatch: pytest.MonkeyPatch):
    calls = {"settings": 0}

    fake_settings = SimpleNamespace(app_name="Startup Check", log_level="INFO")

    def fake_get_settings():
        calls["settings"] += 1
        return fake_settings

    monkeypatch.setattr(main_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(main_module, "configure_logging", lambda _lvl: None)

    app = main_module.create_app()

    with TestClient(app):
        pass

    assert calls["settings"] >= 2


def test_module_level_app_is_fastapi_instance():
    assert isinstance(main_module.app, FastAPI)
