from datetime import datetime
from typing import Any, Literal, Sequence

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.models.agent_entity import Agent
from src.domain.models.history_entity import HistoryMessage
from src.domain.models.user_agent_entity import UserAgent
from src.domain.use_cases.interfaces import IHistoryMessageRepository


class HistoryMessageRepository(IHistoryMessageRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_history_message(
        self, user_agent_id: str, user_message: str, response: str
    ) -> HistoryMessage:
        new_history_message = HistoryMessage(
            user_agent_id=user_agent_id, user_message=user_message, response=response
        )

        self.db.add(new_history_message)
        await self.db.flush()
        return new_history_message

    async def get_history_messages_by_user_agent_id(
        self, user_agent_id: str
    ) -> Sequence[HistoryMessage]:
        query = (
            select(HistoryMessage)
            .options(joinedload(HistoryMessage.message_metadata))
            .where(HistoryMessage.user_agent_id == user_agent_id)
            .order_by(HistoryMessage.created_at.asc())
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_conversation_trend(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ) -> Sequence[Any]:
        """
        Get conversation trend aggregated by period for a user's agents.

        Note: We join:
          HistoryMessage -> UserAgent -> Agent -> User
        """
        # Determine grouping expression
        if group_by == "day":
            group_expr = cast(HistoryMessage.created_at, Date)
        elif group_by == "week":
            group_expr = func.date_trunc("week", HistoryMessage.created_at)
        elif group_by == "month":
            group_expr = func.date_trunc("month", HistoryMessage.created_at)
        else:
            raise ValueError(f"Invalid group_by value: {group_by}. Use day|week|month")

        stmt = (
            select(
                group_expr.label("period"),
                func.count(HistoryMessage.id).label("total_conversations"),
            )
            .select_from(HistoryMessage)
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
