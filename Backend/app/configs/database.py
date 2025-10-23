# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker

# from app.configs.config import settings

# engine = create_engine(
#     settings.DATABASE_URL,
#     connect_args={"check_same_thread": False}
#     if "sqlite" in settings.DATABASE_URL
#     else {},
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.logger import get_logger

from app.configs.config import settings

logger = get_logger(__name__)

# Gunakan async engine
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Gunakan async_sessionmaker untuk AsyncEngine
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


# Dependency untuk FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Import semua model di level module untuk memastikan metadata terdaftar
from app.models import (  # noqa: F401
    Agent,
    ApiKey,
    CompanyInformation,
    Document,
    HistoryMessage,
    Integration,
    Metadata,
    Platform,
    User,
    UserAgent,
)


# Async function untuk membuat tabel
async def create_tables():
    """Create all database tables asynchronously."""
    try:
        async with engine.begin() as conn:
            # Buat semua tabel
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


# Async function untuk menghapus tabel (untuk development/testing)
async def drop_tables():
    """Drop all database tables asynchronously."""
    try:
        async with engine.begin() as conn:
            # Hapus semua tabel
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise
