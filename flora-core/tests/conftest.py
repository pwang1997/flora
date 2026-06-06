import asyncio
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

    async def create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())

    async def override_get_db():
        async with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        async def drop_tables() -> None:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            await engine.dispose()

        asyncio.run(drop_tables())
