from abc import ABC, abstractmethod
from typing import Literal

from src.domain.models.integration_entity import Integration


class IIntergrationRepository(ABC):
    @abstractmethod
    async def add_new_integration(
        self,
        agent_id: str,
        platform: Literal["whatsapp", "telegram", "api"],
        status: Literal["active", "non-active"],
    ) -> Integration:
        pass
