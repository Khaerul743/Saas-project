# auth_controller.py
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import BaseController
from src.app.validators.auth_schema import AuthOutData, LoginIn, RegisterIn
from src.core.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    EmailNotFoundException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    PasswordTooWeakException,
    RemoveTokenError,
    ValidationException,
)
from src.core.exceptions.database_exceptions import DatabaseException
from src.domain.service.auth_service import AuthService


class AuthController(BaseController):
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.auth_service = AuthService(db)

    async def registerHandler(self, payload: RegisterIn) -> AuthOutData:
        """
        Register and create new user with comprehensive error handling.

        Args:
            payload: Registration data

        Returns:
            Dictionary with user data

        Raises:
            Various HTTPExceptions based on specific error types
        """
        try:
            new_user = await self.auth_service.register_user(payload)
            if not new_user:
                raise
            # Log successful registration
            self.logger.info(f"User registration successful: {payload.email}")

            return AuthOutData(name=new_user.name, email=new_user.email)

        except EmailAlreadyExistsException as e:
            # Email already exists - 400 Bad Request
            self.logger.warning(
                f"Registration failed - email already exists: {payload.email}"
            )
            raise e

        except (
            InvalidEmailFormatException,
            PasswordTooWeakException,
            ValidationException,
        ) as e:
            # Validation errors - 400/422 Bad Request/Unprocessable Entity
            self.logger.warning(
                f"Registration failed - validation error: {str(e.detail)}"
            )
            raise e

        except DatabaseException as e:
            # Database errors - 500 Internal Server Error
            self.logger.error(f"Registration failed - database error: {str(e.detail)}")
            raise e

        except Exception as e:
            self.handle_unexpected_error(e)

    async def loginHandler(self, response: Response, payload: LoginIn) -> AuthOutData:
        try:
            user = await self.auth_service.login_handler(response, payload)

            # user authenticated
            self.logger.info(f"User is authenticated: email {user.email}")
            return AuthOutData(email=user.email, name=user.name)

        except (EmailNotFoundException, InvalidCredentialsException):
            # Re-raise custom exceptions
            self.logger.warning(f"Email not found: {payload.email}")
            raise
        except Exception as e:
            # Unexpected errors - 500 Internal Server Error
            self.handle_unexpected_error(e)

    def logoutHandler(self, response: Response, current_user: dict):
        try:
            user = self.auth_service.remove_access_token(response, current_user)
            self.logger.info(f"User {current_user.get('email')} logout successfully")
            return user
        except RemoveTokenError:
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
