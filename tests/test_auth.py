from __future__ import annotations

import pytest

from app.auth.exceptions import ExpiredTokenError, InvalidTokenError, MalformedTokenError, MissingTokenError
from app.auth.service import claims_to_current_user, decode_access_token, extract_bearer_token
from app.config import get_settings


def test_extract_bearer_token_success():
    assert extract_bearer_token("Bearer abc123") == "abc123"


def test_extract_bearer_token_missing():
    with pytest.raises(MissingTokenError):
        extract_bearer_token(None)


def test_extract_bearer_token_malformed():
    with pytest.raises(MalformedTokenError):
        extract_bearer_token("Token abc")


def test_get_current_user_valid(token_factory):
    token = token_factory(sub="u-123")
    claims = decode_access_token(token, get_settings())
    user = claims_to_current_user(claims)
    assert user.id == "u-123"
    assert user.email == "user@example.com"
    assert user.name == "Test User"
    assert user.roles == ["reader"]


def test_get_current_user_expired(token_factory):
    token = token_factory(expired=True)
    with pytest.raises(ExpiredTokenError):
        decode_access_token(token, get_settings())


def test_get_current_user_invalid_signature(token_factory, monkeypatch):
    token = token_factory()
    monkeypatch.setenv("JWT_SECRET_KEY", "different-secret")
    get_settings.cache_clear()
    with pytest.raises(InvalidTokenError):
        decode_access_token(token, get_settings())
