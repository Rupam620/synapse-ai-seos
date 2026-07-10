from __future__ import annotations

from collections.abc import Iterable

from fastapi import FastAPI

import app.main as main_module


def _iter_route_like(route_obj: object) -> Iterable[object]:
    path = getattr(route_obj, "path", None)
    if isinstance(path, str):
        yield route_obj

    original_router = getattr(route_obj, "original_router", None)
    if original_router is not None:
        for nested in getattr(original_router, "routes", []):
            yield from _iter_route_like(nested)


def _all_route_paths(app: FastAPI) -> set[str]:
    paths: set[str] = set()
    for r in app.router.routes:
        for concrete in _iter_route_like(r):
            p = getattr(concrete, "path", None)
            if isinstance(p, str):
                paths.add(p)
    return paths


def test_create_app_returns_fastapi_instance() -> None:
    app = main_module.create_app()
    assert isinstance(app, FastAPI)


def test_create_app_includes_all_declared_router_paths() -> None:
    app = main_module.create_app()
    app_paths = _all_route_paths(app)

    assert "/health" in app_paths
    assert "/backlog" in app_paths
    assert "/users/me" in app_paths
