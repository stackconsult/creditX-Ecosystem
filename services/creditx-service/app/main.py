"""
CreditX Service - Enterprise Production API
Compliance automation with Dragonfly cache and PostgreSQL
"""
import sys
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from python.core_cache import get_cache, DragonflyCache
from python.core_database import get_database, DatabaseClient
from python.core_config import get_settings, Settings
from python.core_logging import setup_logging, get_logger, RequestLogger, set_request_context
from python.core_resilience import circuit_breaker_status

from .routes_compliance import router as compliance_router
from .routes_agents import router as agents_router

logger = get_logger(__name__)

REQUEST_COUNT = Counter(
    "creditx_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "creditx_request_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    settings = get_settings()
    
    setup_logging(
        level=settings.observability.log_level,
        format_type=settings.observability.log_format,
        service_name="creditx-service"
    )
    
    logger.info("Starting CreditX Service", extra={"environment": settings.environment})
    
    try:
        cache = await get_cache()
        logger.info("Dragonfly cache connected")
    except Exception as e:
        logger.warning(f"Cache connection failed (non-fatal): {e}")
    
    try:
        db = await get_database()
        logger.info("PostgreSQL database connected")
    except Exception as e:
        logger.warning(f"Database connection failed (non-fatal): {e}")
    
    yield
    
    logger.info("Shutting down CreditX Service")
    
    try:
        cache = await get_cache()
        await cache.close()
    except Exception:
        pass
    
    try:
        db = await get_database()
        await db.close()
    except Exception:
        pass


app = FastAPI(
    title="CreditX Compliance Service",
    version="2.0.0-dragonfly",
    description="Enterprise compliance automation with AI-powered document processing",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("NODE_ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("NODE_ENV") != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("NODE_ENV") != "production" else [
        "https://ecosystem.ai",
        "https://app.ecosystem.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLogger)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect Prometheus metrics for each request."""
    import time
    start = time.perf_counter()
    
    response = await call_next(request)
    
    latency = time.perf_counter() - start
    endpoint = request.url.path
    method = request.method
    status = response.status_code
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
    
    return response


@app.get("/health/live", tags=["Health"])
async def liveness():
    """Kubernetes liveness probe - is the process running?"""
    return {"status": "ok", "service": "creditx-service"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    """Kubernetes readiness probe - can the service handle traffic?"""
    checks = {"cache": "unknown", "database": "unknown"}
    
    try:
        cache = await get_cache()
        cache_health = await cache.health_check()
        checks["cache"] = cache_health.get("status", "unhealthy")
    except Exception as e:
        checks["cache"] = f"error: {str(e)}"
    
    try:
        db = await get_database()
        db_health = await db.health_check()
        checks["database"] = db_health.get("status", "unhealthy")
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    all_healthy = all(v == "healthy" for v in checks.values())
    
    if not all_healthy:
        raise HTTPException(status_code=503, detail={"status": "degraded", "checks": checks})
    
    return {"status": "ready", "checks": checks}


@app.get("/health/startup", tags=["Health"])
async def startup_probe():
    """Kubernetes startup probe - has the service finished initializing?"""
    return {"status": "started"}


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/status", tags=["Observability"])
async def status():
    """Detailed service status including circuit breakers."""
    settings = get_settings()
    
    cache_metrics = {}
    db_metrics = {}
    
    try:
        cache = await get_cache()
        cache_metrics = cache.metrics.to_dict()
    except Exception:
        pass
    
    try:
        db = await get_database()
        db_metrics = db.metrics.to_dict()
    except Exception:
        pass
    
    return {
        "service": "creditx-service",
        "version": "2.0.0-dragonfly",
        "environment": settings.environment,
        "circuit_breakers": circuit_breaker_status(),
        "cache_metrics": cache_metrics,
        "database_metrics": db_metrics,
    }


app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Compliance"])
app.include_router(agents_router, prefix="/api/v1", tags=["Agents"])
