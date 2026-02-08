"""
Pytest fixtures for PPAS backend tests
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models.user import User
from services.auth_service import AuthService

# Use test database if set, otherwise same as dev (add ?test to avoid collisions)
TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ppas_test"
)




@pytest_asyncio.fixture
async def test_engine():
    """Create test engine and tables"""
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        pool_pre_ping=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a new session for each test, rolled back after test"""
    async with test_engine.connect() as conn:
        await conn.begin()
        async_session = async_sessionmaker(
            conn, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session
        await conn.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """Async HTTP client with overridden DB dependency"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=AuthService.hash_password("password123"),
        name="Test User",
        timezone="UTC"
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user, db_session):
    """Get auth headers for test user"""
    access_token = AuthService.create_access_token(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}
