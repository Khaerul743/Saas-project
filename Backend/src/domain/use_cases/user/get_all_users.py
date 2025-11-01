from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Row

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import UserRepositoryInterface


@dataclass
class GetAllUsersInput:
    page: int
    limit: int


@dataclass
class GetAllUserOutput:
    data_user: Sequence[Row[Any]]
    total: int
    page: int
    limit: int


class GetAllUserPaginate(BaseUseCase[GetAllUsersInput, GetAllUserOutput]):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(
        self, input_data: GetAllUsersInput
    ) -> UseCaseResult[GetAllUserOutput]:
        try:
            offset = (input_data.page - 1) * input_data.limit
            users, total = await self.user_repository.get_users_paginated(
                offset, input_data.limit
            )

            return UseCaseResult.success_result(
                GetAllUserOutput(users, total, input_data.page, input_data.limit)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting users paginate: {str(e)}", e
            )
