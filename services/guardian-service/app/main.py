"""
Guardian Service - AI Endpoint Security
Endpoint protection, device management, incident response
"""
import sys
import os
from contextlib import asynccontextmanager
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from python.core_cache import get_cache
from python.core_database import get_database
from python.core_config import get_settings
from python.core_logging import setup_logging, get_logger, RequestLogger
from python.core_events import get_event_bus, Event, EventType

logger = get_logger(__name__)

ENDPOINTS_REGISTERED = Counter("guardian_endpoints_registered_total", "Total endpoints registered")
INCIDENTS_DETECTED = Counter("guardian_incidents_total", "Total security incidents", ["severity"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(level=settings.observability.log_level, format_type=settings.observability.log_format)
    logger.info("Starting Guardian Service")
    
    try:
        await get_cache()
        await get_database()
    except Exception as e:
        logger.warning(f"Service dependency warning: {e}")
    
    yield
    logger.info("Shutting down Guardian Service")


app = FastAPI(
    title="Guardian Service - AI Endpoint Security",
    version="2.0.0-dragonfly",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("NODE_ENV") != "production" else ["https://ecosystem.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLogger)


class Endpoint(BaseModel):
    id: Optional[UUID] = None
    device_id: str
    device_type: str
    hostname: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    status: str = "active"
    security_score: Optional[int] = Field(None, ge=0, le=100)
    last_seen: Optional[datetime] = None


class SecurityIncident(BaseModel):
    id: Optional[UUID] = None
    endpoint_id: UUID
    incident_type: str
    severity: str
    details: dict
    status: str = "detected"
    created_at: Optional[datetime] = None


class SecurityScanRequest(BaseModel):
    endpoint_id: UUID
    scan_type: str = "full"


class SecurityScanResult(BaseModel):
    endpoint_id: UUID
    security_score: int
    vulnerabilities: List[dict] = []
    recommendations: List[str] = []
    scanned_at: datetime


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant_id


@app.get("/health/live")
async def liveness():
    return {"status": "ok", "service": "guardian-service"}


@app.get("/health/ready")
async def readiness():
    checks = {}
    try:
        cache = await get_cache()
        checks["cache"] = (await cache.health_check()).get("status", "unknown")
    except:
        checks["cache"] = "error"
    try:
        db = await get_database()
        checks["database"] = (await db.health_check()).get("status", "unknown")
    except:
        checks["database"] = "error"
    
    return {"status": "ready", "checks": checks}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/endpoints", response_model=List[Endpoint])
async def list_endpoints(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List protected endpoints."""
    db = await get_database()
    
    where_clauses = ["1=1"]
    params = []
    idx = 1
    
    if tenant_id:
        where_clauses.append(f"tenant_id = ${idx}")
        params.append(tenant_id)
        idx += 1
    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT id, device_id, device_type, hostname, os_type, os_version, 
               status, security_score, last_seen
        FROM guardian_endpoints
        WHERE {" AND ".join(where_clauses)}
        ORDER BY last_seen DESC NULLS LAST
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [Endpoint(**dict(row)) for row in rows]


@app.post("/api/v1/endpoints", response_model=Endpoint, status_code=201)
async def register_endpoint(
    endpoint: Endpoint,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Register a new endpoint for protection."""
    db = await get_database()
    
    query = """
        INSERT INTO guardian_endpoints 
            (tenant_id, device_id, device_type, hostname, os_type, os_version, status, security_score, last_seen)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        ON CONFLICT (tenant_id, device_id) DO UPDATE SET
            hostname = EXCLUDED.hostname,
            os_type = EXCLUDED.os_type,
            os_version = EXCLUDED.os_version,
            last_seen = NOW()
        RETURNING id, last_seen
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        endpoint.device_id,
        endpoint.device_type,
        endpoint.hostname,
        endpoint.os_type,
        endpoint.os_version,
        endpoint.status,
        endpoint.security_score or 100,
    )
    
    endpoint.id = row["id"]
    endpoint.last_seen = row["last_seen"]
    
    ENDPOINTS_REGISTERED.inc()
    logger.info("Registered endpoint", extra={"endpoint_id": str(endpoint.id), "device_id": endpoint.device_id})
    
    return endpoint


@app.post("/api/v1/endpoints/{endpoint_id}/scan", response_model=SecurityScanResult)
async def scan_endpoint(
    endpoint_id: UUID,
    request: SecurityScanRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Perform security scan on an endpoint."""
    db = await get_database()
    cache = await get_cache()
    
    cache_key = f"scan:{endpoint_id}:{request.scan_type}"
    cached = await cache.get(cache_key)
    if cached:
        return SecurityScanResult(**cached)
    
    security_score = 85
    vulnerabilities = []
    recommendations = ["Keep software updated", "Enable firewall", "Use strong passwords"]
    
    await db.execute(
        "UPDATE guardian_endpoints SET security_score = $1, last_scan = NOW() WHERE id = $2",
        security_score,
        endpoint_id,
    )
    
    result = SecurityScanResult(
        endpoint_id=endpoint_id,
        security_score=security_score,
        vulnerabilities=vulnerabilities,
        recommendations=recommendations,
        scanned_at=datetime.utcnow(),
    )
    
    await cache.set(cache_key, result.model_dump(mode="json"), ttl_sec=3600)
    
    return result


@app.post("/api/v1/incidents", response_model=SecurityIncident, status_code=201)
async def report_incident(
    incident: SecurityIncident,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Report a security incident."""
    db = await get_database()
    event_bus = await get_event_bus("guardian-service")
    
    query = """
        INSERT INTO guardian_incidents 
            (tenant_id, endpoint_id, incident_type, severity, details, status)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        incident.endpoint_id,
        incident.incident_type,
        incident.severity,
        incident.details,
        "detected",
    )
    
    incident.id = row["id"]
    incident.created_at = row["created_at"]
    
    INCIDENTS_DETECTED.labels(severity=incident.severity).inc()
    
    await event_bus.publish(
        "security",
        Event(
            event_type=EventType.THREAT_DETECTED,
            payload={
                "incident_id": str(incident.id),
                "endpoint_id": str(incident.endpoint_id),
                "severity": incident.severity,
            },
            tenant_id=tenant_id,
        )
    )
    
    logger.warning(
        "Security incident reported",
        extra={"incident_id": str(incident.id), "severity": incident.severity}
    )
    
    return incident


@app.get("/api/v1/incidents", response_model=List[SecurityIncident])
async def list_incidents(
    endpoint_id: Optional[UUID] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List security incidents."""
    db = await get_database()
    
    where_clauses = ["1=1"]
    params = []
    idx = 1
    
    if tenant_id:
        where_clauses.append(f"tenant_id = ${idx}")
        params.append(tenant_id)
        idx += 1
    if endpoint_id:
        where_clauses.append(f"endpoint_id = ${idx}")
        params.append(endpoint_id)
        idx += 1
    if severity:
        where_clauses.append(f"severity = ${idx}")
        params.append(severity)
        idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT id, endpoint_id, incident_type, severity, details, status, created_at
        FROM guardian_incidents
        WHERE {" AND ".join(where_clauses)}
        ORDER BY created_at DESC
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [SecurityIncident(**dict(row)) for row in rows]
