from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import EmailNotFoundException
from app.repository.user_repository import UserRepository
from app.schema.user_schema import DataUserSchema, UserPaginate
from app.services import BaseService


class UserService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.user_repo = UserRepository(db)

    async def get_all_users(self, page: int, limit: int) -> UserPaginate:
        try:
            offset = (page - 1) * limit
            users, total = await self.user_repo.get_users_paginated(offset, limit)

            # Convert hasil raw ke schema
            users_data = [
                DataUserSchema(
                    id=u.id,
                    name=u.name,
                    email=u.email,
                    role=u.role,
                    job_role=u.job_role,
                    company_name=u.company_name,
                    plan=u.plan,
                    status=u.status,
                    created_at=u.created_at,
                    updated_at=u.updated_at,
                    last_login=u.last_login,
                )
                for u in users
            ]
            self.log_context("Admin getting all users")
            return UserPaginate(
                data_users=users_data, total=total, page=page, limit=limit
            )
        except DatabaseException as e:
            self.handle_database_error(e)

        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting all users paginated", e)

        except Exception as e:
            self.handle_unexpected_error("getting all users", e)
            raise  # Re-raise exception

    async def get_user_by_email(self, email: str):
        try:
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                self.logger.warning(f"User not found: {email}")
                raise EmailNotFoundException(email)
            return user
        except EmailNotFoundException as e:
            self.logger.debug(f"Email not found: {type(e).__name__}")
            raise

        except DatabaseException as e:
            self.handle_database_error(e)

        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Get user by email", e)

        except Exception as e:
            self.handle_unexpected_error("Get user by email", e)
