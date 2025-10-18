# auth_controller.py
from datetime import datetime

from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.dependencies.logger import get_logger
from app.events.redis_event import Event, EventType, event_bus
from app.exceptions import (
    AuthException,
    DatabaseException,
    EmailAlreadyExistsException,
    EmailNotFoundException,
    InvalidCredentialsException,
    InvalidEmailFormatException,
    PasswordTooWeakException,
    ValidationException,
)
from app.models.auth.auth_model import AuthIn, RegisterModel
from app.models.user.user_entity import User
from app.services.auth_service import AuthService
from app.utils.auth_utils import (
    email_exists_handler,
    email_not_found_handler,
    invalid_credentials_handler,
)
from app.utils.hash import hash_password, verify_password
from app.utils.security import create_access_token


class BaseController:
    def __init__(self):
        self.logger = get_logger(__name__)

    def handle_unexpected_error(self, e: Exception):
        self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "field": "server",
            },
        )


class AuthController(BaseController):
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.auth_service = AuthService(db)

    async def registerHandler(self, payload: RegisterModel):
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

            # Log successful registration
            self.logger.info(f"User registration successful: {payload.email}")

            return new_user

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

        except AuthException as e:
            # Other auth-related errors
            self.logger.error(f"Registration failed - auth error: {str(e.detail)}")
            raise e

        except Exception as e:
            self.handle_unexpected_error(e)

    async def loginHandler(self, response: Response, payload: AuthIn):
        try:
            user = await self.auth_service.authenticate_user(response, payload)

            # user authenticated
            self.logger.info(f"User is authenticated: email {user.email}")
            return user
        except (EmailNotFoundException, InvalidCredentialsException):
            # Re-raise custom exceptions
            self.logger.warning(f"Email not found: {payload.email}")
            raise
        except AuthException as e:
            # Other auth-related errors
            self.logger.error(f"login failed - auth error: {str(e.detail)}")
            raise e
        except Exception as e:
            # Unexpected errors - 500 Internal Server Error
            self.handle_unexpected_error(e)


# async def loginHandler(response: Response, db: Session, payload: AuthIn) -> User:
#     """
#     Login user: cek kredensial, buat JWT, simpan di cookie.
#     """
#     # user = db.query(User).filter(User.email == payload.email).first()
#     # # Check if email exists
#     # if not user:
#     #     email_not_found_handler(logger, payload.email)

#     # # Check if password is correct
#     # if not verify_password(payload.password, user.password):
#     #     invalid_credentials_handler(logger, payload.email)

#     try:
#         # access_token = create_access_token(
#         #     {"id": user.id, "email": user.email, "role": user.role}
#         # )
#         # response.set_cookie(
#         #     key="access_token",
#         #     value=access_token,
#         #     httponly=True,
#         #     secure=False,  # True for HTTPS (ngrok)
#         #     samesite="lax",  # Allow cross-site cookies for ngrok
#         #     max_age=3600,  # 1 jam sesuai token expire
#         # )
#         # logger.info(f"User {payload.email} login is successfully.")
#         # return user

#     except Exception as e:
#         logger.exception(f"Unexpected error while creating access token: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error, please try again later",
#         )


def logoutHandler(response: Response, current_user: dict):
    """
    Handler untuk proses logout user.
    Menghapus cookie access_token dan mengembalikan data user.
    """
    try:
        response.delete_cookie(
            "access_token", httponly=True, secure=True, samesite="none"
        )

        logger.info(f"User {current_user.get('email')} logout successfully")
        return current_user
    except Exception as e:
        logger.error(f"Unexpected error while user logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later.",
        )
