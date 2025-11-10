from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal, Sequence

from src.domain.models.history_entity import HistoryMessage


class IHistoryMessageRepository(ABC):
    @abstractmethod
    async def create_history_message(
        self, user_agent_id: str, user_message: str, response: str
    ) -> HistoryMessage:
        pass

    @abstractmethod
    async def get_history_messages_by_user_agent_id(
        self, user_agent_id: str
    ) -> Sequence[HistoryMessage]:
        pass

    @abstractmethod
    async def get_conversation_trend(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ) -> Sequence[Any]:
        """
        Get conversation trend aggregated by period for a user's agents.

        Args:
            user_id: ID of the user
            start_date: Start date for the trend
            end_date: End date for the trend
            group_by: Grouping period (day, week, or month)

        Returns:
            Sequence of query results with period and total_conversations
        """
        pass