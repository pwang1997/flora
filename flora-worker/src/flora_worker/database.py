from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from flora_worker.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
