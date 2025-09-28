import uvicorn
from app.websocket import websocket_route
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
from app.events.redis_event import event_bus
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.limiter_handler import rate_limit_exceeded_handler

# Import Agent after all its related models
from app.models.agent.agent_entity import Agent  # noqa: F401

# Import models that have relationships with Agent first
from app.models.company_information.company_entity import (
    CompanyInformation,  # noqa: F401
)
from app.models.document.document_entity import Document  # noqa: F401

# Import HistoryMessage before UserAgent (UserAgent has relationship to HistoryMessage)
from app.models.history_message.history_entity import HistoryMessage  # noqa: F401
from app.models.history_message.metadata_entity import Metadata  # noqa: F401
from app.models.integration.integration_entity import Integration  # noqa: F401

# Import Platform before Integration (Integration has relationship to Platform)
from app.models.platform.platform_entity import Platform  # noqa: F401
from app.models.user.api_key_entity import ApiKey  # noqa: F401
from app.models.user.user_entity import User  # noqa: F401
from app.models.user_agent.user_agent_entity import UserAgent  # noqa: F401

# Ensure all model mappers are registered before metadata.create_all
from app.routes import (
    agent_route,
    auth_route,
    company_information_route,
    customer_service_route,
    dashboard_route,
    document_route,
    history_route,
    integration_route,
    platform_route,
    simple_rag_route,
    task_route,
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
app.include_router(
    customer_service_route.router
)  # Customer Service Agent specific routes
app.include_router(company_information_route.router)  # Company Information routes
app.include_router(document_route.router)
app.include_router(integration_route.router)
app.include_router(platform_route.router)
app.include_router(history_route.router)
app.include_router(dashboard_route.router)
app.include_router(task_route.router)

# WebSocket routes
app.include_router(websocket_route.router)


@app.on_event("startup")
async def startup_event():
    try:
        await event_bus.start()
        logger.info("Redis event bus started")
    except Exception as e:
        logger.error(f"Error starting Redis event bus: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    try:
        await event_bus.stop_listening()
        logger.info("Redis event bus stopped")
    except Exception as e:
        logger.error(f"Error stopping Redis event bus: {e}")


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(
        status_code=exc.status_code,
        message=exc.detail,
        data=None,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation Error",
        data=exc.errors(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal Server Error",
        data=None,
    )


@app.get("/")
async def root():
    return {"message": "Welcome to SaaS Backend API", "version": settings.VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level="info",
    )
