"""
Custom exceptions for the application
"""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(AppException):
    """Exception raised for validation errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class DatabaseException(AppException):
    """Exception raised for database errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class LLMException(AppException):
    """Exception raised for LLM errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class AgentException(AppException):
    """Exception raised for agent errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class NotFoundException(AppException):
    """Exception raised when resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)
