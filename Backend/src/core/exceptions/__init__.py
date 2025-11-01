from fastapi import HTTPException


class BaseCustomeException(HTTPException):
    """Base exception for errors."""

    pass

# re-export document store exceptions for convenience
from .document_store_exceptions import *  # noqa: F401,F403