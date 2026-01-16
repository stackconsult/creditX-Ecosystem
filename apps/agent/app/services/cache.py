"""Cache service using Dragonfly."""
import redis.asyncio as redis
import structlog
from typing import Optional, Any
import json

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class CacheService:
    """Dragonfly cache service."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Dragonfly."""
        try:
            self._client = redis.Redis(
                host=settings.dragonfly_host,
                port=settings.dragonfly_port,
                password=settings.dragonfly_password or None,
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("Connected to Dragonfly cache")
        except Exception as e:
            logger.warning(f"Failed to connect to cache: {e}, using in-memory fallback")
            self._client = None
    
    async def disconnect(self):
        """Disconnect from Dragonfly."""
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Dragonfly cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._client:
            return None
        try:
            value = await self._client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache."""
        if not self._client:
            return False
        try:
            await self._client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
