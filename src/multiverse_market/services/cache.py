import logging

from redis.asyncio import Redis

from ..interfaces import CacheBackend

logger = logging.getLogger(__name__)


class RedisCache(CacheBackend):
    def __init__(self, redis: Redis) -> None:
        logger.debug("Initializing RedisCache")
        self._redis = redis

    async def get(self, key: str) -> str | None:
        logger.debug(f"Cache lookup for key: {key}")
        return await self._redis.get(key)

    async def setex(self, key: str, expires: int, value: str) -> None:
        logger.debug(f"Setting cache key: {key} with expiry: {expires}s")
        await self._redis.setex(key, expires, value)

    async def delete(self, key: str) -> None:
        logger.debug(f"Deleting cache key: {key}")
        await self._redis.delete(key)
