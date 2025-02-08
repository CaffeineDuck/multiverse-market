"""Integration test fixtures and configuration."""
import logging
from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from multiverse_market.config import Settings
from multiverse_market.dependencies import get_db, get_redis
from multiverse_market.main import app
from multiverse_market.models.entities import Base, Item, Universe, User

logger = logging.getLogger(__name__)

settings = Settings()

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def create_test_db() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
    yield engine
    
    # Cleanup
    await engine.dispose()

# Use a separate Redis database for testing
TEST_REDIS_URL = settings.redis_url.replace("db=0", "db=1")

@pytest_asyncio.fixture(scope="function")
async def test_db(create_test_db: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create session factory using the engine from create_test_db
    async_session = async_sessionmaker(
        create_test_db,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture(scope="function")
async def test_redis() -> AsyncGenerator[Redis, None]:
    """Create a fresh Redis test instance for each test."""
    redis = Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    try:
        await redis.flushdb()
        yield redis
    finally:
        await redis.flushdb()
        await redis.aclose()

@pytest_asyncio.fixture(scope="function")
async def test_app(test_db: AsyncSession, test_redis: Redis) -> AsyncGenerator[AsyncClient, None]:
    """Create a test app with overridden dependencies."""
    async def _override_get_db():
        yield test_db

    async def _override_get_redis():
        yield test_redis

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_redis] = _override_get_redis

    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def setup_test_data(test_db: AsyncSession) -> None:
    """Initialize test data in a single transaction."""
    # Drop and recreate all tables to ensure a clean state
    async with test_db.begin():
        # Get the connection from the session
        connection = await test_db.connection()
        # Drop and recreate all tables
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with test_db.begin():
        try:
            # Create universes
            universes = [
                Universe(id=1, name="Earth", currency_type="USD", exchange_rate=1.0),
                Universe(id=2, name="Mars", currency_type="MRC", exchange_rate=2.5)
            ]
            test_db.add_all(universes)
            await test_db.flush()

            # Create test user
            user = User(id=1, username="test_user", universe_id=1, balance=1000.0)
            test_db.add(user)
            await test_db.flush()

            # Create test items
            items = [
                Item(id=1, name="Earth Item", universe_id=1, price=100.0, stock=10),
                Item(id=2, name="Mars Item", universe_id=2, price=200.0, stock=5)
            ]
            test_db.add_all(items)
            await test_db.flush()

            logger.info("Test data initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing test data: {e}")
            await test_db.rollback()
            raise 