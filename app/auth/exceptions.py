from __future__ import annotations


class AuthError(Exception):
    code: str = "invalid_token"
    message: str = "Invalid authentication token"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class MissingTokenError(AuthError):
    code = "missing_token"
    message = "Missing Authorization header"


class MalformedTokenError(AuthError):
    code = "malformed_token"
    message = "Malformed Authorization header"


class InvalidTokenError(AuthError):
    code = "invalid_token"
    message = "Invalid authentication token"


class ExpiredTokenError(AuthError):
    code = "expired_token"
    message = "Authentication token has expired"
