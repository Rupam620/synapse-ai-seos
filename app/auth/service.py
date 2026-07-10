from __future__ import annotations

from collections.abc import Mapping

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as JwtInvalidTokenError

from app.auth.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    MalformedTokenError,
    MissingTokenError,
)
from app.auth.schemas import CurrentUser
from app.config import Settings, get_settings


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise MissingTokenError()

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise MalformedTokenError()

    return parts[1].strip()


def decode_access_token(token: str, settings: Settings | None = None) -> Mapping[str, object]:
    cfg = settings or get_settings()

    kwargs: dict[str, object] = {
        "algorithms": [cfg.jwt_algorithm],
        "options": {"require": ["exp", "sub"]},
    }
    if cfg.jwt_issuer:
        kwargs["issuer"] = cfg.jwt_issuer
    if cfg.jwt_audience:
        kwargs["audience"] = cfg.jwt_audience

    try:
        decoded = jwt.decode(token, cfg.jwt_secret_key, **kwargs)
    except ExpiredSignatureError as exc:
        raise ExpiredTokenError() from exc
    except JwtInvalidTokenError as exc:
        raise InvalidTokenError() from exc

    if not isinstance(decoded, Mapping):
        raise InvalidTokenError("Invalid token payload")

    return decoded


def claims_to_current_user(claims: Mapping[str, object]) -> CurrentUser:
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        raise InvalidTokenError("Missing or invalid subject claim")

    roles_claim = claims.get("roles", [])
    if isinstance(roles_claim, list):
        roles = [str(r) for r in roles_claim]
    else:
        roles = []

    return CurrentUser(
        id=sub,
        email=claims.get("email") if isinstance(claims.get("email"), str) else None,
        name=claims.get("name") if isinstance(claims.get("name"), str) else None,
        roles=roles,
    )
