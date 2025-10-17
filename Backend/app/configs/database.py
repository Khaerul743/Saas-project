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

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.configs.config import settings

# Gunakan async engine
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Gunakan AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


# Dependency untuk FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
