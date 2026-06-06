import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database import Base
from models.sources import SourceCreate
from repositories.sources.sources_repository import (
    create_source,
    get_source,
    get_source_by_path,
    list_sources,
    update_source,
    delete_source,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_db() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.mark.anyio
async def test_async_crud_operations(async_db: AsyncSession):
    # 1. Create a source
    payload = SourceCreate(
        name="Test Obsidian Vault",
        provider_type="obsidian",
        config={"source_path": "/Users/pwang/test"},
    )
    record = await create_source(async_db, payload)
    assert record.id.startswith("src_")
    assert record.name == "Test Obsidian Vault"
    assert record.config["source_path"] == "/Users/pwang/test"
    await async_db.commit()

    # 2. Get the source by ID
    fetched = await get_source(async_db, record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.name == "Test Obsidian Vault"

    # 3. Get the source by Path
    fetched_by_path = await get_source_by_path(async_db, "/Users/pwang/test")
    assert fetched_by_path is not None
    assert fetched_by_path.id == record.id

    # 4. List sources
    sources = await list_sources(async_db)
    assert len(sources) == 1
    assert sources[0].id == record.id

    # 5. Update source
    updated = await update_source(async_db, record.id, {"name": "Updated Obsidian Vault", "changed_count": 10})
    assert updated is not None
    assert updated.name == "Updated Obsidian Vault"
    assert updated.changed_count == 10
    await async_db.commit()

    # Verify update persisted
    fetched_updated = await get_source(async_db, record.id)
    assert fetched_updated.name == "Updated Obsidian Vault"

    # 6. Delete source
    deleted = await delete_source(async_db, record.id)
    assert deleted is True
    await async_db.commit()

    # Verify deletion
    fetched_deleted = await get_source(async_db, record.id)
    assert fetched_deleted is None

    # Delete non-existent source
    deleted_again = await delete_source(async_db, record.id)
    assert deleted_again is False
