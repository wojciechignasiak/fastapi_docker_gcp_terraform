class CustomException(Exception):
    __slots__ = ('status_code', 'message')
    def __init__(
        self,
        status_code: int,
        message: str | None = None,
    ):
        self.status_code = status_code
        self.message = message


class ServiceError(CustomException):
    """Base exception for service related errors."""

class DataNotFoundError(CustomException):
    """Base exception for service related errors."""

class DatabaseError(CustomException):
    """Base exception for database related errors."""

class LogicError(CustomException):
    """Base exception for other related errors."""
