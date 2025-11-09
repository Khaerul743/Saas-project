from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence

from src.core.exceptions.user_exceptions import UserAgentNotFoundException
from src.domain.models.history_entity import HistoryMessage
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import (
    IHistoryMessageRepository,
    IUserAgentRepository,
)


@dataclass
class GetHistoryMessagesInput:
    user_agent_id: str


@dataclass
class HistoryMessageData:
    user_agent_id: str
    user_message: str
    response: str
    created_at: datetime
    metadata: Optional[dict] = None


@dataclass
class HistoryStats:
    token_usage: int
    response_time: float
    messages: int


@dataclass
class GetHistoryMessagesOutput:
    history_message: List[HistoryMessageData]
    stats: HistoryStats


class GetHistoryMessagesByUserAgentId(
    BaseUseCase[GetHistoryMessagesInput, GetHistoryMessagesOutput]
):
    def __init__(
        self,
        history_message_repository: IHistoryMessageRepository,
        user_agent_repository: IUserAgentRepository,
    ):
        self.history_message_repository = history_message_repository
        self.user_agent_repository = user_agent_repository

    async def execute(
        self, input_data: GetHistoryMessagesInput
    ) -> UseCaseResult[GetHistoryMessagesOutput]:
        try:
            # Validate user agent exists
            user_agent = await self.user_agent_repository.get_user_agent_by_id(
                input_data.user_agent_id
            )
            if not user_agent:
                return UseCaseResult.error_result(
                    "User agent not found",
                    UserAgentNotFoundException(input_data.user_agent_id),
                    "NOT_FOUND",
                )

            # Get history messages
            conversations = (
                await self.history_message_repository.get_history_messages_by_user_agent_id(
                    input_data.user_agent_id
                )
            )

            # If no conversations, return empty result
            if not conversations:
                return UseCaseResult.success_result(
                    GetHistoryMessagesOutput(
                        history_message=[],
                        stats=HistoryStats(token_usage=0, response_time=0.0, messages=0),
                    )
                )

            # Format history messages
            history_data = []
            total_tokens = 0
            total_response_time = 0.0
            metadata_count = 0

            for conv in conversations:
                metadata_dict = None
                if conv.message_metadata:
                    metadata_dict = {
                        "total_tokens": conv.message_metadata.total_tokens,
                        "response_time": conv.message_metadata.response_time,
                        "model": conv.message_metadata.model,
                        "is_success": conv.message_metadata.is_success,
                    }
                    total_tokens += conv.message_metadata.total_tokens
                    total_response_time += conv.message_metadata.response_time
                    metadata_count += 1

                history_data.append(
                    HistoryMessageData(
                        user_agent_id=str(conv.user_agent_id),
                        user_message=str(conv.user_message),
                        response=str(conv.response),
                        created_at=conv.created_at,  # type: ignore
                        metadata=metadata_dict,
                    )
                )

            # Calculate stats
            avg_response_time = (
                round(total_response_time / metadata_count, 2) if metadata_count > 0 else 0.0
            )
            total_messages = len(conversations)

            stats = HistoryStats(
                token_usage=total_tokens,
                response_time=avg_response_time,
                messages=total_messages,
            )

            return UseCaseResult.success_result(
                GetHistoryMessagesOutput(history_message=history_data, stats=stats)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting history messages: {str(e)}", e
            )

