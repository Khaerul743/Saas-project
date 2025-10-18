"""
Custom exceptions package.
"""

from app.exceptions.auth_exceptions import (
    AuthException,
    DatabaseException,
    EmailAlreadyExistsException,
    EmailNotFoundException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    PasswordTooWeakException,
    RemoveTokenError,
    ValidationException,
)

__all__ = [
    "AuthException",
    "EmailAlreadyExistsException",
    "EmailNotFoundException",
    "InvalidCredentialsException",
    "PasswordTooWeakException",
    "InvalidEmailFormatException",
    "DatabaseException",
    "ValidationException",
    "RemoveTokenError",
]
