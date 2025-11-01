from contextvars import ContextVar
from typing import Optional

_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_current_user: ContextVar[Optional[dict]] = ContextVar("current_user", default=None)


class CurrentContext:
    """
    Menyimpan context-level data seperti:
    - request_id
    - current_user (payload JWT)
    yang hidup hanya selama 1 request (thread-safe & async-safe).
    """

    @staticmethod
    def set_request_id(request_id: str):
        _request_id.set(request_id)

    @staticmethod
    def get_request_id() -> Optional[str]:
        return _request_id.get()

    @staticmethod
    def set_current_user(user: dict):
        _current_user.set(user)

    @staticmethod
    def get_current_user() -> Optional[dict]:
        return _current_user.get()

    @staticmethod
    def clear():
        # Reset ContextVar ke default value
        _request_id.set(None)
        _current_user.set(None)
