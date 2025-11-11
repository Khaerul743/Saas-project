from fastapi import status

from src.core.exceptions import BaseCustomeException


class AgentNotFoundException(BaseCustomeException):
    def __init__(self, id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "AGENT_NOT_FOUND",
                "message": "Agent not found, please enter the correct id",
                "field": "id",
                "value": id,
            },
        )


class InvalidApiKeyException(BaseCustomeException):
    def __init__(self, api_key: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_API_KEY",
                "message": "Invalid api key, please enter the correct apikey",
                "field": "apikey",
                "value": api_key,
            },
        )
