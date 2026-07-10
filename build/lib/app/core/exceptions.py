class AppException(Exception):
    def __init__(self, error_code: str, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(error_code="NOT_FOUND", message=message, details=details)


class BadRequestException(AppException):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(error_code="BAD_REQUEST", message=message, details=details)


class ConflictException(AppException):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(error_code="CONFLICT", message=message, details=details)
