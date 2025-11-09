from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.user_schema import (
    DataUserSchema,
    ShowUserProfile,
    UpdateUserPlanOut,
    UserPaginate,
    UserUpdate,
)
from src.core.exceptions.auth_exceptions import NotAuthenticateException
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import (
    EmailNotFoundException,
    UserNotFoundException,
)
from src.domain.repositories.user_repository import UserRepository
from src.domain.service.base import BaseService
from src.domain.use_cases.user import (
    DeleteUser,
    DeleteUserInput,
    GetAllUserPaginate,
    GetAllUsersInput,
    GetUserProfile,
    UpdateUser,
    UpdateUserInput,
    UpdateUserPlan,
    UpdateUserPlanInput,
    UserProfileInput,
)


class UserService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.user_repo = UserRepository(db)
        self.get_users_paginate = GetAllUserPaginate(self.user_repo)
        self.get_user_profile = GetUserProfile(self.user_repo)
        self.update_user_uc = UpdateUser(self.user_repo)
        self.update_user_plan_uc = UpdateUserPlan(self.user_repo)
        self.delete_user_uc = DeleteUser(self.user_repo)

    async def get_all_users(self, page: int, limit: int):
        try:
            get_data = await self.get_users_paginate.execute(
                GetAllUsersInput(page, limit)
            )
            if not get_data.is_success():
                get_exception = get_data.get_exception()
                get_error = get_data.get_error()
                self.logger.warning(
                    f"unexpected error while getting users paginate: {get_error}"
                )
                if get_exception:
                    raise get_exception

            data = get_data.get_data()
            self.log_context("Admin getting all users")

            return data
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
    ):
        try:
            user_email = self.current_user_email()
            if not user_email:
                raise NotAuthenticateException("email", "email not found")

            get_user = await self.get_user_profile.execute(UserProfileInput(user_email))

            if not get_user.is_success():
                get_exception = get_user.get_exception()
                get_error_message = get_user.get_error()
                self.logger.warning(
                    f"Error while get user profile: {get_error_message}"
                )
                if get_exception:
                    raise get_exception

            user_profile = get_user.get_data()
            if not user_profile:
                raise EmailNotFoundException(user_email)
            self.log_context("Show user profile")
            return user_profile.data_user

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
            result = await self.update_user_uc.execute(
                UpdateUserInput(
                    user_id=user_id,
                    name=name,
                    company_name=company_name,
                    job_role=job_role,
                )
            )
            if not result:
                self.logger.warning(
                    f"User not found for update: {user_id} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserNotFoundException(user_id)

            data = result.get_data()
            if not data:
                raise UserNotFoundException(user_id)
            user = data.user
            out = UserUpdate(
                name=str(user.name),
                company_name=user.company_name,
                job_role=user.job_role,
            )
            self.log_context("Updated user profile")

            await self.db.commit()
            return out
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Update user", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("Update user", e)
            raise

    async def update_user_plan(self, user_id: int, plan: str) -> UpdateUserPlanOut:
        try:
            result = await self.update_user_plan_uc.execute(
                UpdateUserPlanInput(user_id=user_id, plan=plan)
            )
            if not result:
                self.logger.warning(
                    f"User not found for plan update: {user_id} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserNotFoundException(user_id)

            data = result.get_data()
            if not data:
                raise UserNotFoundException(user_id)
            user = data.user
            self.log_context(f"Updated user plan: {user.email} -> {plan}")
            await self.db.commit()
            return UpdateUserPlanOut(plan=user.plan, email=str(user.email))
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Update user plan", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("Update user plan", e)
            raise

    async def delete_user(self, user_id: int):
        try:
            result = await self.delete_user_uc.execute(DeleteUserInput(user_id=user_id))
            if not result:
                self.logger.warning(
                    f"User not found for deletion: {user_id} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserNotFoundException(user_id)

            data = result.get_data()
            if not data:
                raise UserNotFoundException(user_id)
            user = data
            self.log_context(f"Deleted user: {user.email}")
            await self.db.commit()
            return user
        except UserNotFoundException as e:
            self.logger.debug(f"User not found: {type(e).__name__}")
            raise
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Delete user", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("Delete user", e)
            raise
