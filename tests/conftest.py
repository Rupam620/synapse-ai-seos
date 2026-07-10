import os
os.environ["JWT_SECRET_KEY"] = "dev-secret-key-for-testing"
os.environ["JWT_ALGORITHM"] = "HS256"

from datetime import datetime, timedelta, timezone
from collections.abc import Generator

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def token_factory():
    def _make_token(
        *,
        sub: str = "user-1",
        email: str | None = "user@example.com",
        name: str | None = "Test User",
        roles: list[str] | None = None,
        expired: bool = False,
        expires_delta_seconds: int = 3600,
        algorithm: str = "HS256",
        secret: str = "dev-secret-key-for-testing",
        issuer: str | None = None,
        audience: str | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        exp = now - timedelta(seconds=60) if expired else now + timedelta(seconds=expires_delta_seconds)

        payload: dict[str, object] = {
            "sub": sub,
            "exp": exp,
            "email": email,
            "name": name,
            "roles": roles if roles is not None else ["reader"],
        }

        if issuer is not None:
            payload["iss"] = issuer
        if audience is not None:
            payload["aud"] = audience

        return jwt.encode(payload, secret, algorithm=algorithm)

    return _make_token
