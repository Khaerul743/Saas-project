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

    @abstractmethod
    async def get_by_agent_and_platform(
        self, agent_id: str, platform: Literal["whatsapp", "telegram", "api"]
    ) -> Integration | None:
        pass

    @abstractmethod
    async def delete_by_id(self, integration_id: int) -> bool:
        pass

    @abstractmethod
    async def get_all_by_agent_id(self, agent_id: str) -> list[Integration]:
        pass