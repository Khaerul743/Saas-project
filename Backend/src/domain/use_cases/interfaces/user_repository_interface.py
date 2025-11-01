from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import Row

from src.domain.models.user_entity import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def create_user(self, name: str, email: str, hashed_password: str):
        pass

    @abstractmethod
    async def get_users_paginated(
        self, offset: int, limit: int
    ) -> tuple[Sequence[Row[Any]], int]:
        pass

    @abstractmethod
    async def update_user(
        self,
        user_id: int,
        name: str | None = None,
        company_name: str | None = None,
        job_role: str | None = None,
    ) -> User | None:
        pass

    @abstractmethod
    async def update_user_plan(self, user_id: int, plan: str) -> User | None:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> User | None:
        pass
