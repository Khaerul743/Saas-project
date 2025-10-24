from logging import Logger
from typing import Optional

from app.core.context import CurrentContext
from app.core.logger import get_logger
from app.exceptions.database_exceptions import DatabaseException


class BaseService:
    def __init__(self, name, request=None):
        self.logger: Logger = get_logger(name)
        self.request = request
        # Jangan ambil context di __init__ karena timing issue
        # Context akan diambil saat dibutuhkan via property

    @property
    def current_user(self) -> Optional[dict]:
        """Lazy loading untuk current_user dari context atau request state"""
        # Coba dari ContextVar dulu
        user = CurrentContext.get_current_user()
        if user is not None:
            print(f"BaseService - Getting current_user from ContextVar: {user}")
            return user

        # Fallback ke request state
        if self.request and hasattr(self.request.state, "current_user"):
            user = self.request.state.current_user
            print(f"BaseService - Getting current_user from request state: {user}")
            return user

        print("BaseService - Getting current_user: None")
        return None

    @property
    def request_id(self):
        """Lazy loading untuk request_id dari context"""
        return CurrentContext.get_request_id()

    def current_user_email(self):
        if self.current_user is not None:
            return self.current_user.get("email", None)
        return None

    def log_context(self, message: str, level: str = "info"):
        """
        Helper logging yang otomatis menyertakan request_id dan user info.
        """
        prefix = f"[request_id={self.request_id}]"
        if self.current_user:
            prefix += f" [user={self.current_user.get('email', 'unknown')}]"

        full_message = f"{prefix} {message}"

        match level.lower():
            case "info":
                self.logger.info(full_message)
            case "warning":
                self.logger.warning(full_message)
            case "error":
                self.logger.error(full_message)
            case _:
                self.logger.debug(full_message)

    def handle_database_error(self, e):
        self.logger.debug(f"Database error: {type(e).__name__}")
        raise e

    def handle_sqlalchemy_error(self, operation: str, e):
        self.logger.error(f"SQLAlchemy error: {str(e)}")
        raise DatabaseException(operation, str(e))

    def handle_unexpected_error(self, field: str, e):
        self.logger.error(f"Unexpected error during {field}: {str(e)}")
        self.logger.error(f"Exception type: {type(e).__name__}")
        self.logger.error(f"Exception args: {e.args}")
        raise
