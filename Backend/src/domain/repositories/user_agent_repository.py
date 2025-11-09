from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user_agent_entity import UserAgent
from src.domain.use_cases.interfaces import IUserAgentRepository


class UserAgentRepository(IUserAgentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_agent_by_id(self, user_agent_id: str) -> UserAgent | None:
        query = select(UserAgent).where(UserAgent.id == user_agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user_agent(
        self,
        id: str,
        agent_id: str,
        username: str,
        user_platform: Literal["telegram"] | Literal["whatsapp"] | Literal["api"],
    ) -> UserAgent:
        new_user_agent = UserAgent(
            id=id, agent_id=agent_id, username=username, user_platform=user_platform
        )

        self.db.add(new_user_agent)
        await self.db.flush()

        return new_user_agent
