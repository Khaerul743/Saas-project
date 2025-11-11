from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.platform_entity import Platform
from src.domain.use_cases.interfaces import IPlatformReporitory


class PlatformRepository(IPlatformReporitory):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_new_platform(
        self,
        integration_id: int,
        platform_type: Literal["telegram"] | Literal["api"] | Literal["whatsapp"],
        api_key: str,
    ) -> Platform:
        new_platform = Platform(
            integration_id=integration_id, platform_type=platform_type, api_key=api_key
        )
        self.db.add(new_platform)
        await self.db.flush()
        await self.db.refresh(new_platform)
        return new_platform
