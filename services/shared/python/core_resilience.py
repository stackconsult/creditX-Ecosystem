"""
Enterprise Resilience Patterns
- Circuit breaker with state machine
- Retry with exponential backoff and jitter
- Timeout management
- Fallback chains
- Bulkhead pattern
"""
import asyncio
import logging
import random
import time
from typing import Callable, TypeVar, Optional, Any, List
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryableError(Exception):
    """Exception that indicates operation should be retried."""
    pass


class NonRetryableError(Exception):
    """Exception that indicates operation should NOT be retried."""
    pass


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = (NonRetryableError, ValueError, TypeError)


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt with exponential backoff and jitter."""
    delay = min(
        config.base_delay_seconds * (config.exponential_base ** attempt),
        config.max_delay_seconds
    )
    
    if config.jitter:
        delay = delay * (0.5 + random.random())
    
    return delay


def retry_async(config: Optional[RetryConfig] = None):
    """Decorator for async retry with exponential backoff."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                
                except config.non_retryable_exceptions as e:
                    logger.warning(
                        f"{func.__name__} failed with non-retryable error: {e}"
                    )
                    raise
                
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1}/{config.max_attempts} "
                            f"failed: {e}. Retrying in {delay:.2f}s"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(config: Optional[RetryConfig] = None):
    """Decorator for sync retry with exponential backoff."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except config.non_retryable_exceptions as e:
                    logger.warning(
                        f"{func.__name__} failed with non-retryable error: {e}"
                    )
                    raise
                
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1}/{config.max_attempts} "
                            f"failed: {e}. Retrying in {delay:.2f}s"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


async def with_timeout(
    coro,
    timeout_seconds: float,
    fallback: Optional[Callable[[], T]] = None,
) -> T:
    """Execute coroutine with timeout and optional fallback."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout_seconds}s")
        if fallback:
            return fallback()
        raise


@dataclass
class BulkheadConfig:
    """Configuration for bulkhead pattern."""
    max_concurrent: int = 10
    max_waiting: int = 100
    timeout_seconds: float = 30.0


class Bulkhead:
    """
    Bulkhead pattern for limiting concurrent executions.
    Prevents one failing service from consuming all resources.
    """
    
    def __init__(self, name: str, config: Optional[BulkheadConfig] = None):
        self.name = name
        self.config = config or BulkheadConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self._waiting = 0
        self._active = 0
    
    @property
    def available(self) -> int:
        return self.config.max_concurrent - self._active
    
    @property
    def waiting(self) -> int:
        return self._waiting
    
    async def execute(self, func: Callable[[], T]) -> T:
        """Execute function within bulkhead limits."""
        if self._waiting >= self.config.max_waiting:
            raise RuntimeError(f"Bulkhead {self.name} queue full")
        
        self._waiting += 1
        try:
            async with asyncio.timeout(self.config.timeout_seconds):
                await self._semaphore.acquire()
                self._waiting -= 1
                self._active += 1
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func()
                    return func()
                finally:
                    self._active -= 1
                    self._semaphore.release()
        except asyncio.TimeoutError:
            self._waiting -= 1
            raise RuntimeError(f"Bulkhead {self.name} timeout")


class FallbackChain:
    """
    Execute operations with fallback chain.
    Tries each operation in order until one succeeds.
    """
    
    def __init__(self, operations: List[Callable[[], T]], name: str = "fallback"):
        self.operations = operations
        self.name = name
    
    async def execute(self) -> T:
        """Execute fallback chain."""
        last_exception = None
        
        for i, operation in enumerate(self.operations):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation()
                return operation()
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Fallback {self.name} operation {i + 1}/{len(self.operations)} "
                    f"failed: {e}"
                )
        
        logger.error(f"All fallback operations failed for {self.name}")
        raise last_exception


def create_circuit_breaker(
    name: str,
    fail_max: int = 5,
    reset_timeout: int = 60,
) -> CircuitBreaker:
    """Create a configured circuit breaker."""
    return CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        name=name,
    )


CIRCUIT_BREAKERS: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a named circuit breaker."""
    if name not in CIRCUIT_BREAKERS:
        CIRCUIT_BREAKERS[name] = create_circuit_breaker(name)
    return CIRCUIT_BREAKERS[name]


def circuit_breaker_status() -> dict:
    """Get status of all circuit breakers."""
    return {
        name: {
            "state": breaker.current_state,
            "fail_counter": breaker.fail_counter,
        }
        for name, breaker in CIRCUIT_BREAKERS.items()
    }
