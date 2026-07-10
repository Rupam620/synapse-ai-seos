from __future__ import annotations

from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as PyJWTInvalidTokenError

from app.auth.exceptions import ExpiredTokenError, InvalidTokenError, MalformedTokenError, MissingTokenError
from app.auth.schemas import CurrentUser
from app.config import Settings, get_settings


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise MissingTokenError()

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise MalformedTokenError('Authorization header must be in the format: Bearer <token>')

    token = parts[1].strip()
    if not token:
        raise MalformedTokenError('Bearer token is empty')

    return token


def decode_access_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    cfg = settings or get_settings()

    options = {'require': ['exp']}
    kwargs: dict[str, Any] = {
        'algorithms': [cfg.jwt_algorithm],
        'options': options,
    }

    if cfg.jwt_algorithm.upper().startswith('HS'):
        key = cfg.jwt_secret_key
    else:
        key = cfg.jwt_secret_key

    if cfg.jwt_issuer:
        kwargs['issuer'] = cfg.jwt_issuer
    if cfg.jwt_audience:
        kwargs['audience'] = cfg.jwt_audience

    try:
        payload = jwt.decode(token, key, **kwargs)
    except ExpiredSignatureError as exc:
        raise ExpiredTokenError() from exc
    except PyJWTInvalidTokenError as exc:
        raise InvalidTokenError() from exc

    if not isinstance(payload, dict):
        raise InvalidTokenError('Invalid token payload')

    if not payload.get('sub'):
        raise InvalidTokenError('Token missing required subject claim')

    return payload


def claims_to_current_user(claims: dict[str, Any]) -> CurrentUser:
    roles_raw = claims.get('roles', [])
    roles = [str(r) for r in roles_raw] if isinstance(roles_raw, list) else []

    return CurrentUser(
        id=str(claims['sub']),
        email=claims.get('email'),
        name=claims.get('name'),
        roles=roles,
        claims=claims,
    )
