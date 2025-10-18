from fastapi import HTTPException, status

from app.dependencies.logger import get_logger


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
