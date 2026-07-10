from __future__ import annotations

from fastapi import Header, HTTPException

from app.auth.exceptions import AuthError
from app.auth.schemas import CurrentUser
from app.auth.service import claims_to_current_user, decode_access_token, extract_bearer_token


def _to_http_401(error: AuthError) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"code": error.code, "message": error.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    try:
        token = extract_bearer_token(authorization)
        claims = decode_access_token(token)
        return claims_to_current_user(claims)
    except AuthError as exc:
        raise _to_http_401(exc) from exc
