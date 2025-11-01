from dataclasses import dataclass

from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.models.user_entity import User
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class UpdateUserPlanInput:
    user_id: int
    plan: str


@dataclass
class UpdateUserPlanOutput:
    user: User


class UpdateUserPlan(BaseUseCase[UpdateUserPlanInput, UpdateUserPlanOutput]):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(
        self, input_data: UpdateUserPlanInput
    ) -> UseCaseResult[UpdateUserPlanOutput]:
        try:
            updated = await self.user_repository.update_user_plan(
                user_id=input_data.user_id, plan=input_data.plan
            )
            if not updated:
                return UseCaseResult.error_result(
                    "User not found", UserNotFoundException(input_data.user_id), "NOT_FOUND"
                )
            return UseCaseResult.success_result(UpdateUserPlanOutput(updated))
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while updating user plan: {str(e)}", e
            )


