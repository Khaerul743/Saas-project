from dataclasses import dataclass

from pydantic import EmailStr

from src.core.exceptions.auth_exceptions import (
    EmailNotFoundException,
    InvalidCredentialsException,
)
from src.core.utils.hash import PasswordHashed
from src.core.utils.security import JWTHandler
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class AuthenticateInput:
    email: str
    password: str


@dataclass
class AuthenticateOutput:
    id: int
    name: str
    email: EmailStr
    password: str
    role: str


class AuthenticateUser(BaseUseCase[AuthenticateInput, AuthenticateOutput]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        jwt_handler: JWTHandler,
        password_hashed: PasswordHashed,
    ):
        self.user_repository = user_repository
        self.jwt_handler = jwt_handler
        self.password_hashed = password_hashed

    async def execute(
        self, input_data: AuthenticateInput
    ) -> UseCaseResult[AuthenticateOutput]:
        try:
            get_user = await self.user_repository.get_user_by_email(input_data.email)
            if not get_user:
                return UseCaseResult.error_result(
                    "User not found", EmailNotFoundException(input_data.email)
                )

            # Verify the user password
            if not self.password_hashed.verify_password(
                input_data.password, get_user.password
            ):
                return UseCaseResult.error_result(
                    "Wrong password", InvalidCredentialsException(get_user.email)
                )

            return UseCaseResult.success_result(
                AuthenticateOutput(
                    get_user.id,
                    get_user.name,
                    get_user.email,
                    get_user.password,
                    get_user.role,
                )
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while authenticate the user: {str(e)}", e
            )
