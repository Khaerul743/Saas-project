from dataclasses import dataclass

from pydantic import EmailStr

from src.core.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    ValidationException,
)
from src.core.utils.hash import PasswordHashed
from src.domain.use_cases.auth.register_validation import (
    RegisterValidation,
    RegisterValidationInput,
)
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class RegisterOut:
    name: str
    email: EmailStr


class RegisterNewUser(BaseUseCase[RegisterValidationInput, RegisterOut]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        register_validation: RegisterValidation,
        password_hashed: PasswordHashed,
    ):
        self.user_repository = user_repository
        self.register_validation = register_validation
        self.password_hashed = password_hashed

    async def execute(
        self, input_data: RegisterValidationInput
    ) -> UseCaseResult[RegisterOut]:
        try:
            data_validation = self.register_validation.validate_input(
                input_data=input_data
            )
            if not data_validation:
                return UseCaseResult.error_result(
                    data_validation.get_error() or "",
                    ValidationException("", data_validation.get_error() or ""),
                    data_validation.get_error_code(),
                )

            validate_data_user = self.register_validation.execute(input_data)
            if not validate_data_user:
                return UseCaseResult.error_result(
                    validate_data_user.get_error() or "",
                    validate_data_user.get_exception(),
                    validate_data_user.get_error_code(),
                )

            # Check if email already exists
            name = input_data.name
            email = input_data.email
            password = input_data.password
            existing_user = await self.user_repository.get_user_by_email(email)
            if existing_user:
                return UseCaseResult.error_result(
                    "Email is already in use",
                    EmailAlreadyExistsException(email),
                    "EMAIL_IN_USE",
                )

            # Hash
            hashed_password = self.password_hashed.hash_password(password)

            # Create new user
            await self.user_repository.create_user(
                name=name, email=email, hashed_password=hashed_password
            )

            return UseCaseResult.success_result(RegisterOut(name=name, email=email))

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while register new user: {str(e)}", e
            )
