from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.integration_entity import Integration
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
        await self.db.flush(new_integration)
        return new_integration
