from dataclasses import dataclass

from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.models.user_entity import User
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class UpdateUserInput:
    user_id: int
    name: str | None = None
    company_name: str | None = None
    job_role: str | None = None


@dataclass
class UpdateUserOutput:
    user: User


class UpdateUser(BaseUseCase[UpdateUserInput, UpdateUserOutput]):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, input_data: UpdateUserInput) -> UseCaseResult[UpdateUserOutput]:
        try:
            updated = await self.user_repository.update_user(
                user_id=input_data.user_id,
                name=input_data.name,
                company_name=input_data.company_name,
                job_role=input_data.job_role,
            )
            if not updated:
                return UseCaseResult.error_result(
                    "User not found", UserNotFoundException(input_data.user_id), "NOT_FOUND"
                )

            return UseCaseResult.success_result(UpdateUserOutput(updated))
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while updating user: {str(e)}", e
            )


