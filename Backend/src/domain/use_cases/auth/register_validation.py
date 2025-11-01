import re
from dataclasses import dataclass
from typing import Any

from src.core.exceptions.auth_exceptions import (
    InvalidEmailFormatException,
    PasswordTooWeakException,
    ValidationException,
)
from src.domain.use_cases.base import BaseUseCase, UseCaseResult


@dataclass
class RegisterValidationInput:
    name: str
    password: str
    email: str


@dataclass
class RegisterValidationOutput:
    name: str
    password: str
    email: str


class RegisterValidation(
    BaseUseCase[RegisterValidationInput, RegisterValidationOutput]
):
    def validate_input(self, input_data: RegisterValidationInput) -> UseCaseResult[Any]:
        if not hasattr(input_data, "name"):
            return UseCaseResult.validation_error("name", "Name is required")
        if not isinstance(input_data.name, str):
            return UseCaseResult.validation_error("name", "Name must be a string")
        if not input_data.name.strip():
            return UseCaseResult.validation_error("name", "Name cannot be empty")

        if not hasattr(input_data, "password"):
            return UseCaseResult.validation_error("password", "Password is required")
        if not isinstance(input_data.password, str):
            return UseCaseResult.validation_error(
                "password", "Password must be a string"
            )
        if not input_data.password.strip():
            return UseCaseResult.validation_error(
                "password", "Password cannot be empty"
            )

        if not hasattr(input_data, "email"):
            return UseCaseResult.validation_error("email", "Email is required")
        if not str(input_data.email).strip():
            return UseCaseResult.validation_error("email", "Email cannot be empty")
        if "@" not in str(input_data.email):
            return UseCaseResult.validation_error("email", "Email is not valid")

        return UseCaseResult.success_result(input_data)

    def execute(self, input_data: RegisterValidationInput):
        try:
            # validate name
            name = input_data.name
            if not name or not isinstance(name, str):
                return UseCaseResult.error_result(
                    "name is required", ValidationException("name", "name is required")
                )

            name = name.strip()
            if len(name) < 2:
                return UseCaseResult.error_result(
                    "name must be at least 2 characters long",
                    ValidationException(
                        "name", "name must be at least 2 characters long"
                    ),
                )

            if len(name) > 50:
                return UseCaseResult.error_result(
                    "name must be less than 50 characters",
                    ValidationException("name", "name must be less than 50 characters"),
                )

            # More flexible character validation - allow spaces and most characters
            if not re.match(r"^[a-zA-Z0-9\s._-]+$", name):
                return UseCaseResult.error_result(
                    "name contains invalid characters",
                    ValidationException("name", "name contains invalid characters"),
                )

            # Validate Email
            if not input_data.email or not isinstance(input_data.email, str):
                return UseCaseResult.error_result(
                    "", InvalidEmailFormatException(""), "INVALID_EMAIL"
                )

            email = input_data.email.strip().lower()

            # Basic email regex pattern
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            if not re.match(email_pattern, email):
                return UseCaseResult.error_result(
                    "Invalid email type",
                    InvalidEmailFormatException(input_data.email),
                    "INVALID_EMAIL",
                )

            # Validate_password
            password = input_data.password
            if not password or not isinstance(password, str):
                return UseCaseResult.error_result(
                    "Password is required",
                    PasswordTooWeakException("Password is required"),
                )

            if len(password) < 6:
                return UseCaseResult.error_result(
                    "Password must be at least 6 characters long",
                    PasswordTooWeakException(
                        "Password must be at least 6 characters long"
                    ),
                )

            if len(password) > 128:
                return UseCaseResult.error_result(
                    "Password must be less than 128 characters",
                    PasswordTooWeakException(
                        "Password must be less than 128 characters"
                    ),
                )

            # Basic validation - just check if it's not too simple
            if password.lower() in [
                "password",
                "123456",
                "qwerty",
                "abc123",
                "admin",
                "user",
            ]:
                return UseCaseResult.error_result(
                    "Password is too common, please choose a more secure password",
                    PasswordTooWeakException(
                        "Password is too common, please choose a more secure password"
                    ),
                )

            return UseCaseResult.success_result(input_data)
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while validate register input: {str(e)}", e
            )
