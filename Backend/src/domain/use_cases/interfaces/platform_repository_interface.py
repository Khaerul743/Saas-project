from abc import ABC, abstractmethod
from typing import Literal

from src.domain.models.platform_entity import Platform


class IPlatformReporitory(ABC):
    @abstractmethod
    async def add_new_platform(
        self,
        integration_id: int,
        platform_type: Literal["telegram", "api", "whatsapp"],
        api_key: str,
    ) -> Platform:
        pass
