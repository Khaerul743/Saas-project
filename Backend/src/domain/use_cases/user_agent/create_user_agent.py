from dataclasses import dataclass
from typing import Literal

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IUserAgentRepository


@dataclass
class CreateUserAgentInput:
    agent_id: str
    unique_id: str
    username: str
    user_platform: Literal["telegram", "whatsapp", "api"]


@dataclass
class CreateUserAgentOutput:
    id: str


class CreateUserAgent(BaseUseCase[CreateUserAgentInput, CreateUserAgentOutput]):
    def __init__(self, user_agent_repository: IUserAgentRepository):
        self.user_agent_repository = user_agent_repository

    async def execute(
        self, input_data: CreateUserAgentInput
    ) -> UseCaseResult[CreateUserAgentOutput]:
        id = input_data.agent_id + input_data.unique_id

        # create agent entity
        await self.user_agent_repository.create_user_agent(
            id, input_data.agent_id, input_data.username, input_data.user_platform
        )

        return UseCaseResult.success_result(CreateUserAgentOutput(id=id))
