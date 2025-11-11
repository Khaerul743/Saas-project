from fastapi import status

from src.core.exceptions import BaseCustomeException


class TelegramApiKeyNotFound(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "TELEGRAM_API_KEY_NOT_FOUND",
                "message": "Telegram api key not found, please enter your telegram api key",
                "field": "telegram api key",
            },
        )


class TelegramResponseException(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail={"error": "failed sending user message"},
        )
