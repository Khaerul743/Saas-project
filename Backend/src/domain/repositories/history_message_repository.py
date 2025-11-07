from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.history_entity import HistoryMessage
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
