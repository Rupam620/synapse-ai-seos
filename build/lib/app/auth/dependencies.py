from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.auth.exceptions import AuthError
from app.auth.schemas import CurrentUser
from app.auth.service import claims_to_current_user, decode_access_token, extract_bearer_token


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    try:
        token = extract_bearer_token(authorization)
        claims = decode_access_token(token)
        return claims_to_current_user(claims)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'code': exc.code, 'message': exc.message},
            headers={'WWW-Authenticate': 'Bearer'},
        ) from exc
