from abc import ABC, abstractmethod
from typing import Literal

from src.domain.models.user_agent_entity import UserAgent


class IUserAgentRepository(ABC):
    @abstractmethod
    async def create_user_agent(
        self,
        id: str,
        agent_id: str,
        username: str,
        user_platform: Literal["telegram", "whatsapp", "api"],
    ) -> UserAgent:
        pass
