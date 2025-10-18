from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.logger import get_logger
from app.models.auth.auth_model import AuthIn, AuthOut, RegisterModel
from app.repository.user_repository import UserRepository
from app.utils.hash import HashingPassword
from app.utils.security import JWTHandler


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(self.db)
        self.jwt = JWTHandler()
        self.hash = HashingPassword()
        self.logger = get_logger(__name__)

    def email_exists_handler(self, email: str):
        """
        Handle error when email is already registered.

        Args:
            logger: Logger instance
            email: Email that already exists
        """
        self.logger.warning(f"Email is already in use: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use."
        )

    async def register_user(self, payload: RegisterModel):
        email = payload.email
        password = payload.password
        name = payload.username
        get_user = await self.user_repo.get_user_by_email(email)
        if get_user:
            return self.email_exists_handler(email)

        hashed_password = self.hash.hash_password(password)
        new_user = await self.user_repo.create_user(
            name=name, email=email, hashed_password=hashed_password
        )
        self.logger.info(f"New user registered with email: {email}")
        return {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "plan": new_user.plan,
        }
