import aioredis
import json
import logging
import os

logger = logging.getLogger(__name__)


class DragonflyCache:
    def __init__(self):
        host = os.getenv("CACHE_HOST", "dragonfly-cache.internal")
        port = os.getenv("CACHE_PORT", "6379")
        db = int(os.getenv("CACHE_DB", "0"))
        self.prefix = os.getenv("CACHE_KEY_PREFIX", "")
        self._dsn = f"redis://{host}:{port}/{db}"
        self._pool = None

    async def connect(self):
        if self._pool is None:
            self._pool = await aioredis.create_redis_pool(
                self._dsn,
                maxsize=int(os.getenv("CACHE_MAX_POOL_SIZE", "50")),
            )
            logger.info("Connected to Dragonfly cache at %s", self._dsn)

    async def close(self):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    def _k(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def get(self, key: str):
        try:
            raw = await self._pool.get(self._k(key))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning("Cache GET failed for %s: %s", key, e)
            return None

    async def set(self, key: str, value, ttl_sec: int = 3600):
        try:
            raw = json.dumps(value)
            await self._pool.setex(self._k(key), ttl_sec, raw)
        except Exception as e:
            logger.warning("Cache SET failed for %s: %s", key, e)

    async def delete(self, key: str):
        try:
            await self._pool.delete(self._k(key))
        except Exception as e:
            logger.warning("Cache DEL failed for %s: %s", key, e)

    async def cache_aside(self, key: str, ttl_sec: int, fetch_fn):
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await fetch_fn()
        await self.set(key, value, ttl_sec)
        return value
