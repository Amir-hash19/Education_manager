import pytest
from httpx import AsyncClient
from app.main import app
from app.db.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

async_engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="function")
async def async_db_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(async_db_session):
    async def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
