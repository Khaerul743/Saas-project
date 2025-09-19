import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.configs.config import settings
from app.configs.database import Base, engine
from app.configs.limiter import limiter
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.limiter_handler import rate_limit_exceeded_handler
from app.models.agent.agent_entity import Agent  # noqa: F401
from app.models.document.document_entity import Document  # noqa: F401
from app.models.history_message.history_entity import HistoryMessage  # noqa: F401
from app.models.history_message.metadata_entity import Metadata  # noqa: F401
from app.models.integration.integration_entity import Integration  # noqa: F401
from app.models.platform.platform_entity import Platform  # noqa: F401
from app.models.user.user_entity import User  # noqa: F401
from app.models.user_agent.user_agent_entity import UserAgent  # noqa: F401
from app.models.user.api_key_entity import ApiKey  # noqa: F401

# Ensure all model mappers are registered before metadata.create_all
from app.routes import (
    agent_route,
    auth_route,
    customer_service_route,
    dashboard_route,
    document_route,
    history_route,
    integration_route,
    platform_route,
    simple_rag_route,
    user_route,
)
from app.utils.logger import get_logger
from app.utils.response import error_response

logger = get_logger(__name__)

# Buat tabel otomatis kalau belum ada (tanpa Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, debug=settings.DEBUG
)

# daftar origin yg diizinkan
origins = [
    settings.FRONTEND_URL,  # Frontend URL from environment
    "http://localhost:3000",  # Frontend development
    "https://localhost:3000",  # Frontend development with HTTPS
    "http://127.0.0.1:3000",  # Alternative localhost
    "https://127.0.0.1:3000",  # Alternative localhost with HTTPS
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # domain yang diizinkan akses
    # allow_origin_regex=".*",
    allow_credentials=True,  # kalau perlu cookie/authorization header
    allow_methods=["*"],  # bolehkan semua HTTP method (GET, POST, dll)
    allow_headers=["*"],
)
# error handler
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(SlowAPIMiddleware)

# tambahin limiter ke state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)



# Routes
app.include_router(user_route.router)
app.include_router(auth_route.router)
app.include_router(agent_route.router)  # General agent routes (get all, etc.)
app.include_router(simple_rag_route.router)  # Simple RAG Agent specific routes
app.include_router(customer_service_route.router)  # Customer Service Agent specific routes
app.include_router(document_route.router)
app.include_router(integration_route.router)
app.include_router(platform_route.router)
app.include_router(history_route.router)
app.include_router(dashboard_route.router)


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
