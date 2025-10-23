from fastapi import HTTPException


class BaseCustomeException(HTTPException):
    """Base exception for errors."""

    pass
