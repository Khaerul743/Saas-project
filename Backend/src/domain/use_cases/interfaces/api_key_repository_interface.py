from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.domain.models.api_key_entity import ApiKey


class IApiKeyRepository(ABC):
    @abstractmethod
    async def create_api_key(
        self,
        user_id: int,
        agent_id: str,
        api_key: str,
        expires_at: Optional[datetime] = None,
    ) -> ApiKey:
        pass
