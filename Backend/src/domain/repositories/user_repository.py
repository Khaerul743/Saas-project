from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user_entity import User
from src.domain.use_cases.interfaces import UserRepositoryInterface


class UserRepository(UserRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_users_paginated(self, offset: int, limit: int):
        """
        Ambil daftar user dengan pagination (raw result).
        """

        stmt = (
            select(
                User.id,
                User.name,
                User.email,
                User.role,
                User.job_role,
                User.company_name,
                User.plan,
                User.status,
                User.created_at,
                User.updated_at,
                User.last_login,
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        users = result.all()  # raw sqlalchemy Row objects

        total_stmt = select(func.count()).select_from(User)
        total_result = await self.db.execute(total_stmt)
        total_users = total_result.scalar_one()

        return users, total_users

    async def create_user(self, name: str, email: str, hashed_password: str):
        new_user = User(name=name, email=email, password=hashed_password)
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(
        self,
        user_id: int,
        name: str | None = None,
        company_name: str | None = None,
        job_role: str | None = None,
    ):
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if name is not None:
            user.name = name  # type: ignore[assignment]
        if company_name is not None:
            user.company_name = company_name  # type: ignore[assignment]
        if job_role is not None:
            user.job_role = job_role  # type: ignore[assignment]

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user_plan(self, user_id: int, plan: str):
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.plan = plan  # type: ignore[assignment]
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        await self.db.delete(user)
        return user
