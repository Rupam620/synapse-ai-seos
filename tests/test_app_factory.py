from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient


@dataclass
class _FakeSettings:
    app_name: str = "Synapse Test App"
    log_level: str = "DEBUG"


def _collect_route_paths(app: Any) -> set[str]:
    """Collect concrete paths from top-level routes and nested included routers."""
    paths: set[str] = set()

    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if isinstance(path, str):
            paths.add(path)

        # Per guidance: traverse nested _IncludedRouter.original_router.routes when present
        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            for nested in getattr(original_router, "routes", []):
                nested_path = getattr(nested, "path", None)
                if isinstance(nested_path, str):
                    paths.add(nested_path)

    return paths


def test_create_app_uses_settings_and_configures_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main

    calls: dict[str, Any] = {"get_settings": 0, "log_level": None}
    fake_settings = _FakeSettings(app_name="QA Factory App", log_level="WARNING")

    def fake_get_settings() -> _FakeSettings:
        calls["get_settings"] += 1
        return fake_settings

    def fake_configure_logging(level: str) -> None:
        calls["log_level"] = level

    monkeypatch.setattr(main, "get_settings", fake_get_settings)
    monkeypatch.setattr(main, "configure_logging", fake_configure_logging)

    app = main.create_app()

    assert app.title == "QA Factory App"
    assert calls["get_settings"] == 1
    assert calls["log_level"] == "WARNING"


def test_startup_event_revalidates_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main

    calls = {"count": 0}
    fake_settings = _FakeSettings()

    def fake_get_settings() -> _FakeSettings:
        calls["count"] += 1
        return fake_settings

    monkeypatch.setattr(main, "get_settings", fake_get_settings)
    monkeypatch.setattr(main, "configure_logging", lambda *_: None)

    app = main.create_app()

    # one call happened during app creation
    assert calls["count"] == 1

    # startup should trigger another get_settings call
    with TestClient(app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200

    assert calls["count"] >= 2


def test_http_exception_handler_returns_expected_shape_and_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main

    monkeypatch.setattr(main, "get_settings", lambda: _FakeSettings())
    monkeypatch.setattr(main, "configure_logging", lambda *_: None)

    app = main.create_app()

    @app.get("/__raise_http_exception")
    def _raise_http_exception() -> None:
        raise HTTPException(
            status_code=401,
            detail={"code": "invalid_token", "message": "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    with TestClient(app) as client:
        response = client.get("/__raise_http_exception")

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "invalid_token", "message": "Invalid token"}
    }
    assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_create_app_includes_health_backlog_and_users_routes() -> None:
    from app.main import app

    paths = _collect_route_paths(app)

    # Validate router inclusion by observable route paths, not router identity.
    # Keep these checks resilient to prefixing by asserting presence of key endpoints.
    assert any("health" in p for p in paths), f"Expected health route in paths: {sorted(paths)}"
    assert any("backlog" in p for p in paths), f"Expected backlog route in paths: {sorted(paths)}"
    assert any("users" in p and "me" in p for p in paths), f"Expected users/me route in paths: {sorted(paths)}"


def test_module_level_app_is_fastapi_instance_with_openapi() -> None:
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert "openapi" in body
    assert "paths" in body
