import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.response import error_response
from src.app.middlewares.context_middleware import ContextMiddleware
from src.app.middlewares.error_handler import ErrorHandlerMiddleware
from src.app.middlewares.limiter_handler import rate_limit_exceeded_handler

# Import routes
from src.app.routes import agent_route, auth_route, simple_rag_route, user_route
from src.config.config import settings
from src.config.database import create_tables
from src.config.limiter import limiter
from src.core.utils.logger import get_logger
from src.domain.events import event_handler
from src.domain.events.redis_event import event_bus

# Import all models to ensure they are registered with SQLAlchemy metadata
# This ensures all tables are created during database initialization
from src.domain.models import *  # noqa: F401, F403

# from app.websocket import ws_route

logger = get_logger(__name__)


# Database tables will be created during startup event


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

# Context
app.add_middleware(ContextMiddleware)

# tambahin limiter ke state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Routes
app.include_router(user_route.router)
app.include_router(auth_route.router)
app.include_router(agent_route.router)  # General agent routes (get all, etc.)
app.include_router(simple_rag_route.router)  # Simple RAG Agent specific routes
# app.include_router(
#     customer_service_route.router
# )  # Customer Service Agent specific routes
# app.include_router(company_information_route.router)  # Company Information routes
# app.include_router(document_route.router)
# app.include_router(integration_route.router)
# app.include_router(platform_route.router)
# app.include_router(history_route.router)
# app.include_router(dashboard_route.router)
# app.include_router(task_route.router)

# WebSocket routes
# app.include_router(ws_route.router)


@app.on_event("startup")
async def startup_event():
    try:
        # Initialize database tables
        await create_tables()
        logger.info("Database tables initialized")

        # Start Redis event bus
        await event_bus.start()
        logger.info("Redis event bus started")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


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


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(
        message="Internal Server Error",
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
