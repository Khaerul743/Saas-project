from dataclasses import dataclass

from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.models.user_entity import User
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class DeleteUserInput:
    user_id: int


class DeleteUser(BaseUseCase[DeleteUserInput, User]):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, input_data: DeleteUserInput) -> UseCaseResult[User]:
        try:
            deleted = await self.user_repository.delete_user(user_id=input_data.user_id)
            if not deleted:
                return UseCaseResult.error_result(
                    "User not found", UserNotFoundException(input_data.user_id), "NOT_FOUND"
                )
            return UseCaseResult.success_result(deleted)
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while deleting user: {str(e)}", e
            )


