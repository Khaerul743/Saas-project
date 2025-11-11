from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.api_key_entity import ApiKey
from src.domain.models.integration_entity import Integration
from src.domain.models.platform_entity import Platform
from src.domain.use_cases.interfaces import IApiKeyRepository


class ApiKeyRepository(IApiKeyRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_api_key(
        self,
        user_id: int,
        agent_id: str,
        api_key: str,
        expires_at: datetime | None = None,
    ) -> ApiKey:
        new_api_key = ApiKey(
            user_id=user_id, agent_id=agent_id, api_key=api_key, expires_at=expires_at
        )

        self.db.add(new_api_key)
        await self.db.flush()
        await self.db.refresh(new_api_key)
        return new_api_key

    async def get_active_api_key(self, agent_id: str, api_key: str) -> ApiKey | None:
        query = select(ApiKey).where(
            ApiKey.api_key == api_key,
            ApiKey.agent_id == agent_id,
            ApiKey.expires_at > datetime.utcnow(),
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_telegram_api_key_by_agent_id(self, agent_id: str) -> str | None:
        """
        Return telegram api_key configured on Platform for a given agent_id.
        """
        stmt = (
            select(Platform.api_key)
            .join(Integration, Platform.integration_id == Integration.id)
            .where(Integration.agent_id == agent_id, Platform.platform_type == "telegram")
        )
        result = await self.db.execute(stmt)
        api_key: str | None = result.scalar_one_or_none()
        return api_key
