from datetime import datetime
from typing import Any, Literal, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.agent_entity import Agent
from src.domain.models.history_entity import HistoryMessage
from src.domain.models.metadata_entity import Metadata
from src.domain.models.user_agent_entity import UserAgent
from src.domain.use_cases.interfaces import IMetadata


class MetadataRepository(IMetadata):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message_metadata(
        self,
        history_message_id: int,
        total_tokens: int,
        response_time: float,
        model: str,
        is_success: bool = True,
    ) -> Metadata:
        new_message_metadata = Metadata(
            history_message_id=history_message_id,
            total_tokens=total_tokens,
            response_time=response_time,
            model=model,
            is_success=is_success,
        )

        self.db.add(new_message_metadata)
        await self.db.flush()
        return new_message_metadata

    async def get_token_usage_trend(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ) -> Sequence[Any]:
        """
        Get token usage trend aggregated by period for a user's agents.

        Note: HistoryMessage does not have agent_id; we join:
          Metadata -> HistoryMessage -> UserAgent -> Agent -> User
        """
        # Decide grouping expression (MySQL-friendly)
        if group_by == "day":
            group_expr = func.date(HistoryMessage.created_at)
        elif group_by == "week":
            # Returns like "21-35" (year-week) which is OK for grouping/ordering as string
            group_expr = func.date_format(HistoryMessage.created_at, "%x-%v")
        elif group_by == "month":
            group_expr = func.date_format(HistoryMessage.created_at, "%Y-%m")
        else:
            raise ValueError(f"Invalid group_by value: {group_by}. Use day|week|month")

        stmt = (
            select(
                group_expr.label("period"),
                func.coalesce(func.sum(Metadata.total_tokens), 0).label("total_tokens"),
            )
            .select_from(Metadata)
            .join(HistoryMessage, Metadata.history_message_id == HistoryMessage.id)
            .join(UserAgent, HistoryMessage.user_agent_id == UserAgent.id)
            .join(Agent, UserAgent.agent_id == Agent.id)
            .where(Agent.user_id == user_id)
            .where(
                HistoryMessage.created_at >= start_date,
                HistoryMessage.created_at <= end_date,
            )
            .group_by(group_expr)
            .order_by(group_expr.asc())
        )

        result = await self.db.execute(stmt)
        return result.all()
