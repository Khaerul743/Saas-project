from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IHistoryMessageRepository


@dataclass
class CreateHistoryMessageInput:
    user_agent_id: str
    user_message: str
    response: str


@dataclass
class CreateHistoryMessageOutput:
    id: int


class CreateHistoryMessage(
    BaseUseCase[CreateHistoryMessageInput, CreateHistoryMessageOutput]
):
    def __init__(self, history_message_repository: IHistoryMessageRepository):
        self.history_message_repository = history_message_repository

    async def execute(
        self, input_data: CreateHistoryMessageInput
    ) -> UseCaseResult[CreateHistoryMessageOutput]:
        # create new history message
        new_history_message = (
            await self.history_message_repository.create_history_message(
                input_data.user_agent_id, input_data.user_message, input_data.response
            )
        )
        return UseCaseResult.success_result(
            CreateHistoryMessageOutput(new_history_message.id)
        )
