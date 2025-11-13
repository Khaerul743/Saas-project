from fastapi import status

from src.core.exceptions import BaseCustomeException


class IntegrationIsAlreadyExist(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INTEGRATION_IS_ALREADY_EXIST",
                "message": "Integration is already exist, please enter different integration platform",
            },
        )


class IntegrationNotFoundException(BaseCustomeException):
    def __init__(self, message: str = "please enter the corrent integration platform."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "INTEGRATION_NOT_FOUND",
                "message": f"Platform integration not found, {message}",
            },
        )


class PlatformDoesntSupportException(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PLATFORM_DOES_NOT_SUPPORT",
                "message": "Please enter the correct platform",
                "platform_available": "telegram, api, whatsapp",
            },
        )


class TelegramApiKeyNotFound(BaseCustomeException):
    def __init__(
        self,
        message: str = "Telegram api key not found, please enter your telegram api key",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "TELEGRAM_API_KEY_NOT_FOUND",
                "message": message,
                "field": "telegram api key",
            },
        )


class TelegramResponseException(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail={"error": "failed sending user message"},
        )
