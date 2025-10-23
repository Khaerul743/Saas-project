from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.context import CurrentContext
from app.utils.generate_random_id import random_uuid4


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = random_uuid4()
        CurrentContext.set_request_id(request_id)
        print(f"ContextMiddleware - Set request_id: {request_id}")

        try:
            response = await call_next(request)
        finally:
            # Bersihkan context agar tidak bocor antar request
            print(f"ContextMiddleware - Before clear: {CurrentContext.get_current_user()}")
            CurrentContext.clear()
            print(f"ContextMiddleware - After clear: {CurrentContext.get_current_user()}")
        
        # Tambahkan request_id ke header response
        response.headers["X-Request-ID"] = request_id
        return response
