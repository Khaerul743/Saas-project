"""
Custom exceptions for authentication operations.
"""

from typing import Optional

from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base exception for authentication errors."""

    pass


class EmailAlreadyExistsException(AuthException):
    """Exception raised when email is already registered."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "EMAIL_ALREADY_EXISTS",
                "message": "Email is already registered",
                "field": "email",
                "value": email,
            },
        )


class EmailNotFoundException(AuthException):
    """Exception raised when email is not found."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EMAIL_NOT_FOUND",
                "message": "Email not found",
                "field": "email",
                "value": email,
            },
        )


class InvalidCredentialsException(AuthException):
    """Exception raised when credentials are invalid."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "field": "credentials",
            },
        )


class PasswordTooWeakException(AuthException):
    """Exception raised when password doesn't meet requirements."""

    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PASSWORD_TOO_WEAK",
                "message": message,
                "field": "password",
            },
        )


class InvalidEmailFormatException(AuthException):
    """Exception raised when email format is invalid."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_EMAIL_FORMAT",
                "message": "Invalid email format",
                "field": "email",
                "value": email,
            },
        )


class DatabaseException(AuthException):
    """Exception raised when database operation fails."""

    def __init__(self, operation: str, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": f"Database {operation} failed: {message}",
                "field": "database",
            },
        )


class ValidationException(AuthException):
    """Exception raised when input validation fails."""

    def __init__(self, field: str, message: str, value: Optional[str] = None):
        detail = {"error": "VALIDATION_ERROR", "message": message, "field": field}
        if value is not None:
            detail["value"] = value

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
