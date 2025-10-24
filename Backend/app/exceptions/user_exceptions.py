from fastapi import status
from pydantic import EmailStr

from app.exceptions import BaseCustomeException


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
