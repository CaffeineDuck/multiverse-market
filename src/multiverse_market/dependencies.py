from typing import AsyncGenerator, Annotated
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends
from .config import settings
from .services import MarketService, RedisCache
from .interfaces import CacheBackend, MarketBackend
from .repositories import (
    UserRepository, ItemRepository,
    TransactionRepository, UniverseRepository
)

# Database setup
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Redis setup
redis = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis() -> AsyncGenerator[Redis, None]:
    """Get Redis connection."""
    try:
        await redis.ping()
        yield redis
    finally:
        await redis.close()

async def get_cache_backend(redis: Redis = Depends(get_redis)) -> CacheBackend:
    """Get cache backend."""
    return RedisCache(redis)

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository."""
    return UserRepository(db)

async def get_item_repository(db: AsyncSession = Depends(get_db)) -> ItemRepository:
    """Get item repository."""
    return ItemRepository(db)

async def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    """Get transaction repository."""
    return TransactionRepository(db)

async def get_universe_repository(db: AsyncSession = Depends(get_db)) -> UniverseRepository:
    """Get universe repository."""
    return UniverseRepository(db)

async def get_market_service(
    users: UserRepository = Depends(get_user_repository),
    items: ItemRepository = Depends(get_item_repository),
    transactions: TransactionRepository = Depends(get_transaction_repository),
    universes: UniverseRepository = Depends(get_universe_repository),
    cache: CacheBackend = Depends(get_cache_backend)
) -> MarketBackend:
    """Get market service instance."""
    return MarketService(users, items, transactions, universes, cache)

# Dependency types
UserRepositoryDependency = Annotated[UserRepository, Depends(get_user_repository)]
ItemRepositoryDependency = Annotated[ItemRepository, Depends(get_item_repository)]
TransactionRepositoryDependency = Annotated[TransactionRepository, Depends(get_transaction_repository)]
UniverseRepositoryDependency = Annotated[UniverseRepository, Depends(get_universe_repository)]
CacheDependency = Annotated[CacheBackend, Depends(get_cache_backend)]
MarketDependency = Annotated[MarketBackend, Depends(get_market_service)]