from __future__ import annotations


class AuthError(Exception):
    code = 'invalid_token'
    message = 'Invalid authentication token'

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class MissingTokenError(AuthError):
    code = 'missing_token'
    message = 'Missing bearer token'


class MalformedTokenError(AuthError):
    code = 'malformed_token'
    message = 'Malformed bearer token'


class InvalidTokenError(AuthError):
    code = 'invalid_token'
    message = 'Invalid authentication token'


class ExpiredTokenError(AuthError):
    code = 'expired_token'
    message = 'Authentication token has expired'
