from redis.asyncio import Redis
from ..interfaces import CacheBackend

class RedisCache(CacheBackend):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis
    
    async def get(self, key: str) -> str | None:
        return await self._redis.get(key)
    
    async def setex(self, key: str, expires: int, value: str) -> None:
        await self._redis.setex(key, expires, value)
    
    async def delete(self, key: str) -> None:
        await self._redis.delete(key) 