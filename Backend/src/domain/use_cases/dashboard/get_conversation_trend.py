from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal

from src.core.exceptions.auth_exceptions import ValidationException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import (
    IHistoryMessageRepository,
    UserRepositoryInterface,
)


@dataclass
class GetConversationTrendInput:
    user_id: int
    start_date: datetime
    end_date: datetime
    group_by: Literal["day", "week", "month"]


@dataclass
class ConversationTrendItem:
    period: str
    total_conversations: int


@dataclass
class GetConversationTrendOutput:
    trend: List[ConversationTrendItem]


class GetConversationTrend(BaseUseCase[GetConversationTrendInput, GetConversationTrendOutput]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        history_message_repository: IHistoryMessageRepository,
    ):
        self.user_repository = user_repository
        self.history_message_repository = history_message_repository

    def _format_conversation_trend_data(self, results: List) -> List[ConversationTrendItem]:
        """
        Format conversation trend data from database query results.

        Args:
            results: Raw query results from database

        Returns:
            List of ConversationTrendItem containing period and total_conversations
        """
        trend = [
            ConversationTrendItem(
                period=str(r.period.date() if hasattr(r.period, "date") else r.period),
                total_conversations=int(r.total_conversations or 0),
            )
            for r in results
        ]
        return trend

    async def execute(
        self, input_data: GetConversationTrendInput
    ) -> UseCaseResult[GetConversationTrendOutput]:
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(input_data.user_id)
            if not user:
                return UseCaseResult.error_result(
                    "User not found",
                    UserNotFoundException(input_data.user_id),
                    "USER_NOT_FOUND",
                )

            # Validate group_by
            if input_data.group_by not in ["day", "week", "month"]:
                return UseCaseResult.error_result(
                    "Invalid group_by value. Use day|week|month",
                    ValidationException("group_by", "Invalid group_by value"),
                    "INVALID_GROUP_BY",
                )

            # Validate date range
            if input_data.start_date > input_data.end_date:
                return UseCaseResult.error_result(
                    "Start date must be before end date",
                    ValidationException("date_range", "Start date must be before end date"),
                    "INVALID_DATE_RANGE",
                )

            # Get conversation trend from repository
            results = await self.history_message_repository.get_conversation_trend(
                user_id=input_data.user_id,
                start_date=input_data.start_date,
                end_date=input_data.end_date,
                group_by=input_data.group_by,
            )

            # Format results
            trend = self._format_conversation_trend_data(list(results))

            return UseCaseResult.success_result(GetConversationTrendOutput(trend=trend))

        except ValueError as e:
            return UseCaseResult.error_result(
                str(e), ValidationException("group_by", str(e)), "INVALID_GROUP_BY"
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting conversation trend: {str(e)}", e
            )

