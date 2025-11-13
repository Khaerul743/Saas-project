from typing import Literal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models.integration_entity import Integration
from src.domain.use_cases.interfaces import IIntergrationRepository


class IntegrationRepository(IIntergrationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_new_integration(
        self,
        agent_id: str,
        platform: Literal["whatsapp"] | Literal["telegram"] | Literal["api"],
        status: Literal["active"] | Literal["non-active"],
    ) -> Integration:
        new_integration = Integration(
            agent_id=agent_id, platform=platform, status=status
        )
        self.db.add(new_integration)
        await self.db.flush()
        await self.db.refresh(new_integration)
        return new_integration

    async def get_by_agent_and_platform(
        self, agent_id: str, platform: Literal["whatsapp", "telegram", "api"]
    ) -> Integration | None:
        stmt = select(Integration).where(
            Integration.agent_id == agent_id, Integration.platform == platform
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, integration_id: int) -> bool:
        stmt = delete(Integration).where(Integration.id == integration_id)
        await self.db.execute(stmt)
        # Caller should commit
        return True

    async def get_all_by_agent_id(self, agent_id: str) -> list[Integration]:
        stmt = (
            select(Integration)
            .where(Integration.agent_id == agent_id)
            .options(selectinload(Integration.platform_config))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
