# auth_service.py
from typing import Literal

from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.core.utils.hash import PasswordHashed
from src.core.utils.security import JWTHandler
from src.domain.repositories import UserRepository
from src.domain.service import BaseService
from src.domain.use_cases.auth import (
    AuthenticateInput,
    AuthenticateUser,
    RegisterNewUser,
    RegisterValidation,
    RegisterValidationInput,
)


class AuthService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(__name__)
        self.db = db
        self.user_repo = UserRepository(self.db)
        self.jwt = JWTHandler()
        self.hash = PasswordHashed()
        self.register_validation = RegisterValidation()
        self.register_new_user = RegisterNewUser(
            self.user_repo, self.register_validation, self.hash
        )
        self.authenticate_user = AuthenticateUser(self.user_repo, self.jwt, self.hash)
        self.key = "access_token"
        self.httponly = True
        self.secure = False
        self.samesite: Literal["lax", "strict", "none"] = "lax"

    async def register_user(self, payload: RegisterIn):
        """
        Register a new user with proper validation and error handling.

        Args:
            payload: Registration data

        Returns:
            Dictionary with user data

        Raises:
            EmailAlreadyExistsException: If email is already registered
            DatabaseException: If database operation fails
            Various validation exceptions: If input data is invalid
        """
        try:
            input_data = RegisterValidationInput(
                name=payload.name, password=payload.password, email=payload.email
            )

            # Delegate validation and creation to use case
            reg_user = await self.register_new_user.execute(input_data)
            if not reg_user:
                self.logger.warning(
                    f"Register user failed: code={reg_user.get_error_code()} error={reg_user.get_error()}"
                )
                get_exception = reg_user.get_exception()
                if get_exception:
                    raise get_exception
                raise ValidationException("", reg_user.get_error() or "Unknown error")

            user = reg_user.get_data()
            return AuthOutData(name=str(user.name), email=str(user.email))
        except EmailAlreadyExistsException as e:
            # Email already exists
            self.logger.debug(f"Email already exists: {type(e).__name__}")
            raise
        except (
            InvalidEmailFormatException,
            PasswordTooWeakException,
            ValidationException,
        ) as e:
            # Validation errors
            self.logger.debug(f"Validation error: {type(e).__name__}")
            raise
        except DatabaseException as e:
            # Database errors
            self.handle_database_error(e)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Get user", e)
        except Exception as e:
            self.handle_unexpected_error("Register new user", e)

    async def login_handler(self, response: Response, payload: LoginIn):
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            User object if authentication successful

        Raises:
            EmailNotFoundException: If email is not found
            InvalidCredentialsException: If password is incorrect
            DatabaseException: If database operation fails
        """
        try:
            auth_user = await self.authenticate_user.execute(
                AuthenticateInput(payload.email, payload.password)
            )

            if not auth_user:
                self.logger.warning(
                    f"{payload.email} login failed: {auth_user.get_error()}"
                )
                get_exception = auth_user.get_exception()
                if get_exception:
                    raise get_exception

            # Set cookie
            get_data_user = auth_user.get_data()
            if get_data_user:
                user_data = {
                    "id": get_data_user.id,
                    "email": get_data_user.email,
                    "role": get_data_user.role,
                }
            else:
                raise

            access_token = self.jwt.create_access_token(user_data)
            response.set_cookie(
                key=self.key,
                value=access_token,
                httponly=self.httponly,
                secure=self.secure,  # True (HTTPS)
                samesite=self.samesite,
                max_age=3600,  # One hour
            )

            return get_data_user
        except (EmailNotFoundException, InvalidCredentialsException):
            # Re-raise custom exceptions
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Get user", e)
        except Exception as e:
            self.handle_unexpected_error("Authenticate user", e)

    def remove_access_token(self, response: Response, current_user: dict):
        try:
            response.delete_cookie(
                self.key,
                httponly=self.httponly,
                secure=self.secure,
                samesite=self.samesite,
            )
            return current_user
        except Exception as e:
            self.logger.error(f"Unexpected error while user logout: {str(e)}")
            raise RemoveTokenError()
