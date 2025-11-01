from dataclasses import dataclass

from src.core.exceptions.user_exceptions import EmailNotFoundException
from src.domain.models.user_entity import User
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class UserProfileInput:
    email: str


@dataclass
class UserProfileOutput:
    data_user: User


class GetUserProfile(BaseUseCase[UserProfileInput, UserProfileOutput]):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(
        self, input_data: UserProfileInput
    ) -> UseCaseResult[UserProfileOutput]:
        try:
            get_user = await self.user_repository.get_user_by_email(input_data.email)
            if not get_user:
                return UseCaseResult.error_result(
                    "User not found", EmailNotFoundException(input_data.email)
                )

            return UseCaseResult.success_result(UserProfileOutput(get_user))
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while get user profile: {str(e)}", e
            )
