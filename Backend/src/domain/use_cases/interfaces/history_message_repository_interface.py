from abc import ABC, abstractmethod
from typing import Any, Sequence

from src.domain.models.history_entity import HistoryMessage


class IHistoryMessageRepository(ABC):
    @abstractmethod
    async def create_history_message(
        self, user_agent_id: str, user_message: str, response: str
    ) -> HistoryMessage:
        pass
