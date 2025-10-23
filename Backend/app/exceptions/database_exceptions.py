from fastapi import status

from app.exceptions import BaseCustomeException


class DatabaseException(BaseCustomeException):
    """Exception raised when database operation fails."""

    def __init__(self, operation: str, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": f"Database {operation} failed: {message}",
                "field": "database",
            },
        )
