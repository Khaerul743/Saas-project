from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.api_key_entity import ApiKey
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
        return new_api_key
