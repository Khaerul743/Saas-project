import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.configs.config import settings
from app.configs.database import Base, engine
from app.configs.limiter import limiter
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.limiter_handler import rate_limit_exceeded_handler
from app.routes import user_route
from app.utils.logger import get_logger
from app.utils.response import error_response

logger = get_logger(__name__)

# Buat tabel otomatis kalau belum ada (tanpa Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, debug=settings.DEBUG
)

# tambahin limiter ke state
app.state.limiter = limiter
# register handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(user_route.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.PROJECT_NAME} v{settings.VERSION}"}


# Handler untuk HTTPException
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.detail),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "fail",
            "message": "Validation error.",
            "errors": exc.errors(),
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)
