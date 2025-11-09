from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.core.utils.logger import get_logger
from src.core.exceptions.database_exceptions import DatabaseException


class BaseController:
    def __init__(self):
        self.logger = get_logger(__name__)
        self._internal_server_error = status.HTTP_500_INTERNAL_SERVER_ERROR

    # def handle_database_error(self, e: DatabaseException, message: str):
    #     self.logger.error(f"Database error: {str(e)}", exc_info=True)
    #     raise HTTPException(
    #         status_code=self._internal_server_error,
    #         detail={
    #             "error": "INTERNAL_SERVER_ERROR",
    #             "message": message,
    #             "field": "database",
    #         },
    #     )

    # def handle_sqlalchemy_error(self, e: SQLAlchemyError, message: str):
    #     self.logger.error(f"SQLalchemy error: {str(e)}", exc_info=True)
    #     raise HTTPException(
    #         status_code=self._internal_server_error,
    #         detail={
    #             "error": "INTERNAL_SERVER_ERROR",
    #             "message": message,
    #             "field": "orm",
    #         },
    #     )

    def handle_unexpected_error(self, e: Exception):
        self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=self._internal_server_error,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "field": "server",
            },
        )
