"""
Validation utilities for input data.
"""

import re
from typing import Optional

from app.exceptions.auth_exceptions import (
    InvalidEmailFormatException,
    PasswordTooWeakException,
    ValidationException,
)


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email to validate

    Returns:
        Validated email

    Raises:
        InvalidEmailFormatException: If email format is invalid
    """
    if not email or not isinstance(email, str):
        raise InvalidEmailFormatException("")

    email = email.strip().lower()

    # Basic email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        raise InvalidEmailFormatException(email)

    return email


def validate_password(password: str) -> str:
    """
    Validate password strength with relaxed requirements.

    Args:
        password: Password to validate

    Returns:
        Validated password

    Raises:
        PasswordTooWeakException: If password doesn't meet basic requirements
    """
    if not password or not isinstance(password, str):
        raise PasswordTooWeakException("Password is required")

    if len(password) < 6:
        raise PasswordTooWeakException("Password must be at least 6 characters long")

    if len(password) > 128:
        raise PasswordTooWeakException("Password must be less than 128 characters")

    # Basic validation - just check if it's not too simple
    if password.lower() in ["password", "123456", "qwerty", "abc123", "admin", "user"]:
        raise PasswordTooWeakException(
            "Password is too common, please choose a more secure password"
        )

    return password


def validate_username(username: str) -> str:
    """
    Validate username with relaxed requirements.

    Args:
        username: Username to validate

    Returns:
        Validated username

    Raises:
        ValidationException: If username is invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationException("username", "Username is required")

    username = username.strip()

    if len(username) < 2:
        raise ValidationException(
            "username", "Username must be at least 2 characters long"
        )

    if len(username) > 50:
        raise ValidationException(
            "username", "Username must be less than 50 characters"
        )

    # More flexible character validation - allow spaces and most characters
    if not re.match(r"^[a-zA-Z0-9\s._-]+$", username):
        raise ValidationException("username", "Username contains invalid characters")

    return username


def validate_register_data(email: str, password: str, username: str) -> dict:
    """
    Validate all registration data.

    Args:
        email: Email to validate
        password: Password to validate
        username: Username to validate

    Returns:
        Dictionary with validated data

    Raises:
        Various validation exceptions if data is invalid
    """
    return {
        "email": validate_email(email),
        "password": validate_password(password),
        "username": validate_username(username),
    }
