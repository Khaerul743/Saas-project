from typing import Literal

from fastapi import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.logger import get_logger
from app.exceptions import (
    DatabaseException,
    EmailAlreadyExistsException,
    EmailNotFoundException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    PasswordTooWeakException,
    RemoveTokenError,
    ValidationException,
)
from app.repository.user_repository import UserRepository
from app.schema.auth_schema import AuthOutData, LoginIn, RegisterIn
from app.utils.hash import HashingPassword
from app.utils.security import JWTHandler
from app.utils.validation import validate_register_data


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(self.db)
        self.jwt = JWTHandler()
        self.hash = HashingPassword()
        self.logger = get_logger(__name__)
        self.key = "access_token"
        self.httponly = True
        self.secure = False
        self.samesite: Literal["lax", "strict", "none"] = "lax"

    async def register_user(self, payload: RegisterIn) -> AuthOutData:
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
            # Validate input data
            self.logger.debug(
                f"Validating registration data for email: {payload.email}"
            )
            validated_data = validate_register_data(
                payload.email, payload.password, payload.name
            )
            self.logger.debug("Validation passed successfully")

            email = validated_data["email"]
            password = validated_data["password"]
            name = validated_data["username"]

            # Check if email already exists
            existing_user = await self.user_repo.get_user_by_email(email)
            if existing_user:
                self.logger.warning(
                    f"Registration attempt with existing email: {email}"
                )
                raise EmailAlreadyExistsException(email)

            # Hash password
            hashed_password = self.hash.hash_password(password)

            # Create user
            new_user = await self.user_repo.create_user(
                name=name, email=email, hashed_password=hashed_password
            )

            self.logger.info(f"New user registered successfully: {email}")
            return AuthOutData(name=str(new_user.name), email=str(new_user.email))
            # return {
            #     "id": new_user.id,
            #     "name": new_user.name,
            #     "email": new_user.email,
            #     "plan": new_user.plan,
            # }

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
            self.logger.debug(f"Database error: {type(e).__name__}")
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"SQLAlchemy error during user registration: {str(e)}")
            raise DatabaseException("user creation", str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error during user registration: {str(e)}")
            self.logger.error(f"Exception type: {type(e).__name__}")
            self.logger.error(f"Exception args: {e.args}")
            raise DatabaseException("user creation", "An unexpected error occurred")

    async def authenticate_user(
        self, response: Response, payload: LoginIn
    ) -> AuthOutData:
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
            email = payload.email
            password = payload.password
            # Get user by email
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                self.logger.warning(f"Login attempt with non-existent email: {email}")
                raise EmailNotFoundException(email)

            # Verify password
            if not self.hash.verify_password(password, user.password):
                self.logger.warning(f"Invalid password attempt for email: {email}")
                raise InvalidCredentialsException(email)

            # Set cookie
            data = {"id": user.id, "email": user.email, "role": user.role}
            access_token = self.jwt.create_access_token(data)
            response.set_cookie(
                key=self.key,
                value=access_token,
                httponly=self.httponly,
                secure=self.secure,  # True (HTTPS)
                samesite=self.samesite,
                max_age=3600,  # One hour
            )

            self.logger.info(f"User authenticated successfully: {email}")
            return AuthOutData(name=str(user.name), email=str(user.email))

        except (EmailNotFoundException, InvalidCredentialsException):
            # Re-raise custom exceptions
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"Database error during user authentication: {str(e)}")
            raise DatabaseException("user authentication", str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error during user authentication: {str(e)}")
            raise DatabaseException(
                "user authentication", "An unexpected error occurred"
            )

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
