"""
Enterprise-grade Dragonfly Cache Client
- Redis-compatible using modern redis-py (aioredis deprecated)
- Circuit breaker for resilience
- Connection pooling with health checks
- Structured logging with metrics
- Cache-aside pattern with stampede protection
"""
import json
import logging
import os
import asyncio
from typing import Any, Callable, Optional, TypeVar
from datetime import datetime
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheMetrics:
    """Track cache performance metrics for observability."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.latency_sum_ms = 0.0
        self.operation_count = 0
    
    def record_hit(self, latency_ms: float):
        self.hits += 1
        self.latency_sum_ms += latency_ms
        self.operation_count += 1
    
    def record_miss(self, latency_ms: float):
        self.misses += 1
        self.latency_sum_ms += latency_ms
        self.operation_count += 1
    
    def record_error(self):
        self.errors += 1
    
    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def avg_latency_ms(self) -> float:
        return self.latency_sum_ms / self.operation_count if self.operation_count > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_ratio": round(self.hit_ratio, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
        }


class DragonflyCache:
    """
    Enterprise-grade Dragonfly cache client with:
    - Async connection pooling
    - Circuit breaker pattern
    - Cache-aside with stampede protection
    - Prometheus-ready metrics
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: int = 0,
        prefix: str = "",
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        self.host = host or os.getenv("CACHE_HOST", "dragonfly-cache.internal")
        self.port = port or int(os.getenv("CACHE_PORT", "6379"))
        self.db = db or int(os.getenv("CACHE_DB_MAIN", "0"))
        self.prefix = prefix or os.getenv("CACHE_KEY_PREFIX", "")
        self.max_connections = max_connections or int(os.getenv("CACHE_MAX_POOL_SIZE", "50"))
        self.socket_timeout = socket_timeout or float(os.getenv("CACHE_TIMEOUT_MS", "5000")) / 1000
        
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._connected = False
        
        self._breaker = CircuitBreaker(
            fail_max=circuit_breaker_threshold,
            reset_timeout=circuit_breaker_timeout,
            name="dragonfly_cache",
        )
        
        self.metrics = CacheMetrics()
        self._locks: dict[str, asyncio.Lock] = {}
    
    async def connect(self) -> None:
        """Initialize connection pool to Dragonfly."""
        if self._connected:
            return
        
        try:
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_timeout,
                decode_responses=True,
                health_check_interval=30,
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            await self._client.ping()
            self._connected = True
            logger.info(
                "Connected to Dragonfly cache",
                extra={"host": self.host, "port": self.port, "db": self.db}
            )
        except Exception as e:
            logger.error("Failed to connect to Dragonfly: %s", e)
            raise
    
    async def close(self) -> None:
        """Gracefully close all connections."""
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.disconnect()
        self._connected = False
        logger.info("Dragonfly cache connection closed")
    
    async def health_check(self) -> dict:
        """Health check for readiness probes."""
        try:
            start = datetime.now()
            await self._client.ping()
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "circuit_breaker": self._breaker.current_state,
                "metrics": self.metrics.to_dict(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _key(self, key: str) -> str:
        """Apply prefix to key."""
        return f"{self.prefix}{key}" if self.prefix else key
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with circuit breaker protection."""
        start = datetime.now()
        try:
            raw = await self._breaker.call_async(self._client.get, self._key(key))
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            
            if raw is None:
                self.metrics.record_miss(latency_ms)
                return None
            
            self.metrics.record_hit(latency_ms)
            return json.loads(raw)
        
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.warning("Cache circuit breaker OPEN for GET %s", key)
            return None
        except json.JSONDecodeError:
            self.metrics.record_error()
            logger.warning("Cache JSON decode failed for %s", key)
            return None
        except Exception as e:
            self.metrics.record_error()
            logger.warning("Cache GET failed for %s: %s", key, e)
            return None
    
    async def set(self, key: str, value: Any, ttl_sec: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            raw = json.dumps(value, default=str)
            await self._breaker.call_async(
                self._client.setex, self._key(key), ttl_sec, raw
            )
            return True
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.warning("Cache circuit breaker OPEN for SET %s", key)
            return False
        except Exception as e:
            self.metrics.record_error()
            logger.warning("Cache SET failed for %s: %s", key, e)
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self._breaker.call_async(self._client.delete, self._key(key))
            return True
        except CircuitBreakerError:
            logger.warning("Cache circuit breaker OPEN for DELETE %s", key)
            return False
        except Exception as e:
            logger.warning("Cache DEL failed for %s: %s", key, e)
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (use sparingly)."""
        try:
            cursor = 0
            deleted = 0
            full_pattern = self._key(pattern)
            
            while True:
                cursor, keys = await self._client.scan(cursor, match=full_pattern, count=100)
                if keys:
                    deleted += await self._client.delete(*keys)
                if cursor == 0:
                    break
            
            return deleted
        except Exception as e:
            logger.warning("Cache DELETE PATTERN failed for %s: %s", pattern, e)
            return 0
    
    async def cache_aside(
        self,
        key: str,
        fetch_fn: Callable[[], T],
        ttl_sec: int = 3600,
        stampede_lock_timeout: float = 5.0,
    ) -> Optional[T]:
        """
        Cache-aside pattern with stampede protection.
        Only one caller fetches on miss; others wait.
        """
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        lock = self._locks[key]
        
        try:
            async with asyncio.timeout(stampede_lock_timeout):
                async with lock:
                    cached = await self.get(key)
                    if cached is not None:
                        return cached
                    
                    if asyncio.iscoroutinefunction(fetch_fn):
                        value = await fetch_fn()
                    else:
                        value = fetch_fn()
                    
                    await self.set(key, value, ttl_sec)
                    return value
        
        except asyncio.TimeoutError:
            logger.warning("Cache stampede lock timeout for %s", key)
            if asyncio.iscoroutinefunction(fetch_fn):
                return await fetch_fn()
            return fetch_fn()
        finally:
            if key in self._locks and not lock.locked():
                del self._locks[key]
    
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to Dragonfly pub/sub channel."""
        try:
            raw = json.dumps(message, default=str)
            return await self._client.publish(channel, raw)
        except Exception as e:
            logger.warning("Cache PUBLISH failed for %s: %s", channel, e)
            return 0
    
    async def xadd(self, stream: str, data: dict, maxlen: int = 10000) -> Optional[str]:
        """Add entry to Dragonfly stream (Redis Streams compatible)."""
        try:
            return await self._client.xadd(stream, data, maxlen=maxlen)
        except Exception as e:
            logger.warning("Cache XADD failed for %s: %s", stream, e)
            return None


_cache_instance: Optional[DragonflyCache] = None


async def get_cache() -> DragonflyCache:
    """Get singleton cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DragonflyCache()
        await _cache_instance.connect()
    return _cache_instance


@asynccontextmanager
async def cache_lifespan():
    """Context manager for FastAPI lifespan."""
    cache = await get_cache()
    yield cache
    await cache.close()
