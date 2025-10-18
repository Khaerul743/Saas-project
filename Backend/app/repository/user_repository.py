from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user.user_entity import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, name: str, email: str, hashed_password: str):
        new_user = User(name=name, email=email, password=hashed_password)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
