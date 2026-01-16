"""Health check routes."""
from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter()


@router.get("/live")
async def liveness():
    """Liveness probe."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness(request: Request):
    """Readiness probe."""
    cache_healthy = request.app.state.cache._client is not None
    
    return {
        "status": "ready" if cache_healthy else "degraded",
        "checks": {
            "cache": "healthy" if cache_healthy else "unhealthy",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
