from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.metadata_entity import Metadata
from src.domain.use_cases.interfaces import IMetadata


class MetadataRepository(IMetadata):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message_metadata(
        self,
        history_message_id: int,
        total_tokens: int,
        response_time: float,
        model: str,
        is_success: bool = True,
    ) -> Metadata:
        new_message_metadata = Metadata(
            history_message_id=history_message_id,
            total_tokens=total_tokens,
            response_time=response_time,
            model=model,
            is_success=is_success,
        )

        self.db.add(new_message_metadata)
        await self.db.flush()
        return new_message_metadata
