"""
Enterprise-grade PostgreSQL Database Client
- Async connection pooling with asyncpg
- Circuit breaker for resilience
- Multi-tenant schema support
- Health checks and metrics
- Transaction management
"""
import logging
import os
import asyncio
from typing import Any, Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Pool, Connection
from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)


class DatabaseMetrics:
    """Track database performance metrics for observability."""
    
    def __init__(self):
        self.queries = 0
        self.errors = 0
        self.latency_sum_ms = 0.0
        self.active_connections = 0
        self.pool_size = 0
    
    def record_query(self, latency_ms: float):
        self.queries += 1
        self.latency_sum_ms += latency_ms
    
    def record_error(self):
        self.errors += 1
    
    @property
    def avg_latency_ms(self) -> float:
        return self.latency_sum_ms / self.queries if self.queries > 0 else 0.0
    
    def to_dict(self) -> dict:
        return {
            "queries": self.queries,
            "errors": self.errors,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "active_connections": self.active_connections,
            "pool_size": self.pool_size,
        }


class DatabaseClient:
    """
    Enterprise-grade PostgreSQL client with:
    - Async connection pooling (asyncpg)
    - Circuit breaker pattern
    - Multi-tenant schema support
    - Prometheus-ready metrics
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        min_connections: int = 5,
        max_connections: int = 20,
        command_timeout: float = 60.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        self._raw_url = database_url or os.getenv("DATABASE_URL", "")
        self._dsn = self._parse_dsn(self._raw_url)
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.command_timeout = command_timeout
        
        self._pool: Optional[Pool] = None
        self._connected = False
        
        self._breaker = CircuitBreaker(
            fail_max=circuit_breaker_threshold,
            reset_timeout=circuit_breaker_timeout,
            name="postgresql_db",
        )
        
        self.metrics = DatabaseMetrics()
    
    def _parse_dsn(self, url: str) -> str:
        """Convert SQLAlchemy URL to asyncpg DSN format."""
        if url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql://")
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://")
        return url
    
    async def connect(self) -> None:
        """Initialize connection pool."""
        if self._connected:
            return
        
        try:
            self._pool = await asyncpg.create_pool(
                self._dsn,
                min_size=self.min_connections,
                max_size=self.max_connections,
                command_timeout=self.command_timeout,
                server_settings={
                    "application_name": "creditx-ecosystem",
                    "jit": "off",
                },
            )
            self._connected = True
            self.metrics.pool_size = self.max_connections
            logger.info("Connected to PostgreSQL", extra={"pool_size": self.max_connections})
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL: %s", e)
            raise
    
    async def close(self) -> None:
        """Gracefully close all connections."""
        if self._pool:
            await self._pool.close()
        self._connected = False
        logger.info("PostgreSQL connection pool closed")
    
    async def health_check(self) -> dict:
        """Health check for readiness probes."""
        try:
            start = datetime.now()
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "circuit_breaker": self._breaker.current_state,
                "pool_size": self._pool.get_size(),
                "pool_free": self._pool.get_idle_size(),
                "metrics": self.metrics.to_dict(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @asynccontextmanager
    async def acquire(self, tenant_id: Optional[str] = None):
        """
        Acquire connection from pool with optional tenant schema.
        Sets search_path for multi-tenant isolation.
        """
        start = datetime.now()
        conn: Connection = None
        try:
            conn = await self._pool.acquire()
            self.metrics.active_connections += 1
            
            if tenant_id:
                schema = f"tenant_{tenant_id}"
                await conn.execute(f"SET search_path TO {schema}, public")
            
            yield conn
            
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            self.metrics.record_query(latency_ms)
        
        except Exception as e:
            self.metrics.record_error()
            logger.error("Database connection error: %s", e)
            raise
        finally:
            if conn:
                self.metrics.active_connections -= 1
                await self._pool.release(conn)
    
    @asynccontextmanager
    async def transaction(self, tenant_id: Optional[str] = None):
        """Execute operations within a transaction."""
        async with self.acquire(tenant_id) as conn:
            async with conn.transaction():
                yield conn
    
    async def execute(
        self,
        query: str,
        *args,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)."""
        start = datetime.now()
        try:
            async with self.acquire(tenant_id) as conn:
                result = await self._breaker.call_async(conn.execute, query, *args)
                latency_ms = (datetime.now() - start).total_seconds() * 1000
                self.metrics.record_query(latency_ms)
                return result
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.error("Database circuit breaker OPEN")
            raise
    
    async def fetch(
        self,
        query: str,
        *args,
        tenant_id: Optional[str] = None,
    ) -> List[asyncpg.Record]:
        """Fetch multiple rows."""
        start = datetime.now()
        try:
            async with self.acquire(tenant_id) as conn:
                rows = await self._breaker.call_async(conn.fetch, query, *args)
                latency_ms = (datetime.now() - start).total_seconds() * 1000
                self.metrics.record_query(latency_ms)
                return rows
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.error("Database circuit breaker OPEN")
            raise
    
    async def fetchrow(
        self,
        query: str,
        *args,
        tenant_id: Optional[str] = None,
    ) -> Optional[asyncpg.Record]:
        """Fetch single row."""
        start = datetime.now()
        try:
            async with self.acquire(tenant_id) as conn:
                row = await self._breaker.call_async(conn.fetchrow, query, *args)
                latency_ms = (datetime.now() - start).total_seconds() * 1000
                self.metrics.record_query(latency_ms)
                return row
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.error("Database circuit breaker OPEN")
            raise
    
    async def fetchval(
        self,
        query: str,
        *args,
        tenant_id: Optional[str] = None,
    ) -> Any:
        """Fetch single value."""
        start = datetime.now()
        try:
            async with self.acquire(tenant_id) as conn:
                val = await self._breaker.call_async(conn.fetchval, query, *args)
                latency_ms = (datetime.now() - start).total_seconds() * 1000
                self.metrics.record_query(latency_ms)
                return val
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.error("Database circuit breaker OPEN")
            raise
    
    async def executemany(
        self,
        query: str,
        args: List[tuple],
        tenant_id: Optional[str] = None,
    ) -> None:
        """Execute query with multiple parameter sets (batch insert)."""
        start = datetime.now()
        try:
            async with self.acquire(tenant_id) as conn:
                await self._breaker.call_async(conn.executemany, query, args)
                latency_ms = (datetime.now() - start).total_seconds() * 1000
                self.metrics.record_query(latency_ms)
        except CircuitBreakerError:
            self.metrics.record_error()
            logger.error("Database circuit breaker OPEN")
            raise
    
    async def create_tenant_schema(self, tenant_id: str) -> None:
        """Create isolated schema for a new tenant."""
        schema = f"tenant_{tenant_id}"
        async with self.acquire() as conn:
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            logger.info("Created tenant schema: %s", schema)
    
    async def run_migrations(self, migrations_dir: str) -> None:
        """Run SQL migration files in order."""
        import os
        import glob
        
        migration_files = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))
        
        async with self.transaction() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            applied = await conn.fetch("SELECT filename FROM _migrations")
            applied_set = {r["filename"] for r in applied}
            
            for filepath in migration_files:
                filename = os.path.basename(filepath)
                if filename not in applied_set:
                    with open(filepath, "r") as f:
                        sql = f.read()
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO _migrations (filename) VALUES ($1)",
                        filename
                    )
                    logger.info("Applied migration: %s", filename)


_db_instance: Optional[DatabaseClient] = None


async def get_database() -> DatabaseClient:
    """Get singleton database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseClient()
        await _db_instance.connect()
    return _db_instance


@asynccontextmanager
async def database_lifespan():
    """Context manager for FastAPI lifespan."""
    db = await get_database()
    yield db
    await db.close()
