from abc import ABC, abstractmethod
from typing import Any, Sequence

from src.domain.models.metadata_entity import Metadata


class IMetadata(ABC):
    @abstractmethod
    async def create_message_metadata(
        self,
        history_message_id: int,
        total_tokens: int,
        response_time: float,
        model: str,
        is_success: bool = True,
    ) -> Metadata:
        pass
