from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.domain.models.api_key_entity import ApiKey


class IApiKeyRepository(ABC):
    @abstractmethod
    async def get_api_key_by_agent_id(self, agent_id: str) -> ApiKey | None:
        pass

    @abstractmethod
    async def create_api_key(
        self,
        user_id: int,
        agent_id: str,
        api_key: str,
        expires_at: Optional[datetime] = None,
    ) -> ApiKey:
        pass

    @abstractmethod
    async def get_active_api_key(self, agent_id: str, api_key: str) -> ApiKey | None:
        pass

    @abstractmethod
    async def get_telegram_api_key_by_agent_id(self, agent_id: str) -> str | None:
        pass

    @abstractmethod
    async def delete_api_key_by_agent_id(self, agent_id: str):
        pass
