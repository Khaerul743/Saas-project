from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal, Sequence

from src.domain.models.metadata_entity import Metadata


class IMetadata(ABC):
    @abstractmethod
    async def create_message_metadata(
        self,
        history_message_id: int,
        total_tokens: int,
        response_time: float,
        model: str,
        is_success: bool = True,
    ) -> Metadata:
        pass

    @abstractmethod
    async def get_token_usage_trend(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ) -> Sequence[Any]:
        """
        Get token usage trend aggregated by period for a user's agents.

        Args:
            user_id: ID of the user
            start_date: Start date for the trend
            end_date: End date for the trend
            group_by: Grouping period (day, week, or month)

        Returns:
            Sequence of query results with period and total_tokens
        """
        pass
