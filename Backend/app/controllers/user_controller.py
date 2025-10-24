from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import BaseController
from app.exceptions.database_exceptions import DatabaseException
from app.exceptions.user_exceptions import EmailNotFoundException, UserNotFoundException
from app.schema.user_schema import UpdateUserPlanOut, UserPaginate, UserUpdate
from app.services.user_service import UserService


class UserController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.user_service = UserService(db, request)

    async def get_all_users(self, page: int, limit: int) -> UserPaginate:
        try:
            data_users = await self.user_service.get_all_users(page, limit)
            return data_users

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

    async def get_user_profile(self):
        try:
            user_profile = await self.user_service.get_user_by_email()
            return user_profile

        except EmailNotFoundException as e:
            raise e

        except DatabaseException as e:
            raise e

        except SQLAlchemyError as e:
            raise e

        except Exception as e:
            self.handle_unexpected_error(e)
            raise
