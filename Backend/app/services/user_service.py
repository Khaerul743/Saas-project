from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.auth_exceptions import NotAuthenticateException
from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import EmailNotFoundException, UserNotFoundException
from app.repository.user_repository import UserRepository
from app.schema.user_schema import (
    DataUserSchema,
    ShowUserProfile,
    UpdateUserPlanOut,
    UserPaginate,
    UserUpdate,
)
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
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting all users paginated", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("getting all users", e)
            raise  # Re-raise exception

    async def get_user_by_email(
        self,
    ) -> ShowUserProfile:
        try:
            user_email = self.current_user_email()
            if not user_email:
                raise NotAuthenticateException("email", "email not found")

            user = await self.user_repo.get_user_by_email(user_email)
            if not user:
                self.logger.warning(f"User not found: {user_email}")
                raise EmailNotFoundException(user_email)

            user = ShowUserProfile(
                id=user.id,
                name=str(user.name),
                email=str(user.email),
                company_name=str(user.company_name),
                plan=str(user.plan),
                job_role=str(user.job_role),
            )
            self.log_context("Show user profile")
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
            raise

    async def update_user(
        self,
        user_id: int,
        name: str | None = None,
        company_name: str | None = None,
        job_role: str | None = None,
    ) -> UserUpdate:
        try:
            user = await self.user_repo.update_user(
                user_id, name, company_name, job_role
            )
            if not user:
                self.logger.warning(f"User not found for update: {user_id}")
                raise UserNotFoundException(user_id)

            user = UserUpdate(
                name=str(user.name),
                company_name=user.company_name,
                job_role=user.job_role,
            )

            self.log_context("Updated user profile")
            return user
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Update user", e)
        except Exception as e:
            self.handle_unexpected_error("Update user", e)
            raise

    async def update_user_plan(self, user_id: int, plan: str) -> UpdateUserPlanOut:
        try:
            user = await self.user_repo.update_user_plan(user_id, plan)
            if not user:
                self.logger.warning(f"User not found for plan update: {user_id}")
                raise UserNotFoundException(user_id)

            self.log_context(f"Updated user plan: {user.email} -> {plan}")
            user = UpdateUserPlanOut(plan=user.plan, email=str(user.email))
            return user
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Update user plan", e)
        except Exception as e:
            self.handle_unexpected_error("Update user plan", e)
            raise

    async def delete_user(self, user_id: int):
        try:
            user = await self.user_repo.delete_user(user_id)
            if not user:
                self.logger.warning(f"User not found for deletion: {user_id}")
                raise UserNotFoundException(user_id)

            self.log_context(f"Deleted user: {user.email}")
            return user
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Delete user", e)
        except Exception as e:
            self.handle_unexpected_error("Delete user", e)
            raise
