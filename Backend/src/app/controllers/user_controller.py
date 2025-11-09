from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.user_schema import (
    DataUserSchema,
    ShowUserProfile,
    UpdateUserPlanOut,
    UserPaginate,
    UserUpdate,
)
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import (
    EmailNotFoundException,
    UserNotFoundException,
)
from src.domain.service.user_service import UserService


class UserController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.user_service = UserService(db, request)

    async def get_all_users(self, page: int, limit: int) -> UserPaginate:
        try:
            data_users = await self.user_service.get_all_users(page, limit)
            if not data_users:
                raise
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
                for u in data_users.data_user
            ]
            return UserPaginate(
                data_users=users_data,
                total=data_users.total,
                page=page,
                limit=data_users.limit,
            )

        except DatabaseException as e:
            raise e
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise  # Re-raise exception

    async def update_user(
        self,
        user_id: int,
        name: str | None = None,
        company_name: str | None = None,
        job_role: str | None = None,
    ) -> UserUpdate:
        try:
            updated_user = await self.user_service.update_user(
                user_id, name, company_name, job_role
            )
            return updated_user
        except UserNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def update_user_plan(self, user_id: int, plan: str) -> UpdateUserPlanOut:
        try:
            updated_user = await self.user_service.update_user_plan(user_id, plan)
            return updated_user
        except UserNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def delete_user(self, user_id: int):
        try:
            deleted_user = await self.user_service.delete_user(user_id)
            return deleted_user
        except UserNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def get_user_profile(self) -> ShowUserProfile:
        try:
            user_profile = await self.user_service.get_user_by_email()
            if not user_profile:
                raise
            return ShowUserProfile(
                id=user_profile.id,
                name=user_profile.name,
                email=user_profile.email,
                company_name=user_profile.company_name,
                plan=user_profile.plan,
                job_role=user_profile.job_role,
            )

        except EmailNotFoundException as e:
            raise e

        except DatabaseException as e:
            raise e

        except SQLAlchemyError as e:
            raise e

        except Exception as e:
            self.handle_unexpected_error(e)
            raise
