"""
Enterprise Structured Logging
- JSON format for production
- Correlation IDs for tracing
- Prometheus metrics integration
- Request context propagation
"""
import logging
import sys
import json
import time
import uuid
from typing import Optional, Any, Dict
from contextvars import ContextVar
from datetime import datetime
from functools import wraps

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
tenant_id_var: ContextVar[str] = ContextVar("tenant_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "tenant_id": tenant_id_var.get(),
            "user_id": user_id_var.get(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        for key in ["host", "path", "method", "status_code", "latency_ms", "service"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        return json.dumps(log_data, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        request_id = request_id_var.get()
        prefix = f"[{request_id[:8]}] " if request_id else ""
        return f"{color}{record.levelname:8}{self.RESET} {prefix}{record.getMessage()}"


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    service_name: str = "creditx-ecosystem",
) -> None:
    """Configure logging for the application."""
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    handler = logging.StreamHandler(sys.stdout)
    
    if format_type == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())
    
    root_logger.addHandler(handler)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


def set_request_context(
    request_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> str:
    """Set context variables for the current request."""
    rid = request_id or str(uuid.uuid4())
    request_id_var.set(rid)
    if tenant_id:
        tenant_id_var.set(tenant_id)
    if user_id:
        user_id_var.set(user_id)
    return rid


def clear_request_context() -> None:
    """Clear context variables after request completion."""
    request_id_var.set("")
    tenant_id_var.set("")
    user_id_var.set("")


def log_execution_time(logger: Optional[logging.Logger] = None):
    """Decorator to log function execution time."""
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{func.__name__} completed",
                    extra={"latency_ms": round(elapsed_ms, 2), "function": func.__name__}
                )
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{func.__name__} failed: {e}",
                    extra={"latency_ms": round(elapsed_ms, 2), "function": func.__name__}
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{func.__name__} completed",
                    extra={"latency_ms": round(elapsed_ms, 2), "function": func.__name__}
                )
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{func.__name__} failed: {e}",
                    extra={"latency_ms": round(elapsed_ms, 2), "function": func.__name__}
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class RequestLogger:
    """ASGI middleware for request logging."""
    
    def __init__(self, app, logger: Optional[logging.Logger] = None):
        self.app = app
        self.logger = logger or logging.getLogger("http")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start = time.perf_counter()
        
        request_id = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"x-request-id":
                request_id = header_value.decode()
                break
        
        request_id = set_request_context(request_id=request_id)
        
        status_code = 500
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            path = scope.get("path", "")
            method = scope.get("method", "")
            
            if not path.startswith("/health"):
                self.logger.info(
                    f"{method} {path} {status_code}",
                    extra={
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "latency_ms": round(elapsed_ms, 2),
                    }
                )
            
            clear_request_context()
