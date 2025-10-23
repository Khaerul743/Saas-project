from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user.user_entity import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
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
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
