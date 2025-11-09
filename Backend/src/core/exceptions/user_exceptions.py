from fastapi import status
from pydantic import EmailStr

from src.core.exceptions import BaseCustomeException


class EmailNotFoundException(BaseCustomeException):
    def __init__(self, email: EmailStr):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "EMAIL_NOT_FOUND",
                "message": "User not found",
                "field": "email",
                "value": email,
            },
        )


class UserNotFoundException(BaseCustomeException):
    def __init__(self, id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "USER_NOT_FOUND",
                "message": "User not found",
                "field": "id",
                "value": id,
            },
        )


class UserAgentNotFoundException(BaseCustomeException):
    def __init__(self, user_agent_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "USER_AGENT_NOT_FOUND",
                "message": "User agent not found",
                "field": "user_agent_id",
                "value": user_agent_id,
            },
        )