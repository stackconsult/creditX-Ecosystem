"""
Threat Service - Global AI Alert Network
Threat detection, anomaly analysis, security alerting
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
from python.core_ai import get_ai_router, Message, ModelCapability

logger = get_logger(__name__)

REQUEST_COUNT = Counter("threat_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
ALERTS_CREATED = Counter("threat_alerts_created_total", "Total alerts created", ["severity"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(level=settings.observability.log_level, format_type=settings.observability.log_format)
    logger.info("Starting Threat Service")
    
    try:
        await get_cache()
        await get_database()
        await get_event_bus("threat-service")
    except Exception as e:
        logger.warning(f"Service dependency connection warning: {e}")
    
    yield
    logger.info("Shutting down Threat Service")


app = FastAPI(
    title="Threat Service - Global AI Alert Network",
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


class ThreatAlert(BaseModel):
    id: Optional[UUID] = None
    alert_type: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    title: str
    description: Optional[str] = None
    source: str
    affected_entities: List[dict] = []
    indicators: dict = {}
    status: str = "open"
    created_at: Optional[datetime] = None


class ThreatAnalysisRequest(BaseModel):
    data: dict
    context: Optional[str] = None
    

class ThreatAnalysisResponse(BaseModel):
    threat_detected: bool
    severity: str
    confidence: float
    analysis: str
    recommendations: List[str] = []


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant_id


@app.get("/health/live")
async def liveness():
    return {"status": "ok", "service": "threat-service"}


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


@app.get("/api/v1/alerts", response_model=List[ThreatAlert])
async def list_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List threat alerts with filtering."""
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
    if severity:
        where_clauses.append(f"severity = ${idx}")
        params.append(severity)
        idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT id, alert_type, severity, title, description, source, 
               affected_entities, indicators, status, created_at
        FROM threat_alerts
        WHERE {" AND ".join(where_clauses)}
        ORDER BY created_at DESC
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [ThreatAlert(**dict(row)) for row in rows]


@app.post("/api/v1/alerts", response_model=ThreatAlert, status_code=201)
async def create_alert(
    alert: ThreatAlert,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Create a new threat alert."""
    db = await get_database()
    event_bus = await get_event_bus("threat-service")
    
    query = """
        INSERT INTO threat_alerts 
            (tenant_id, alert_type, severity, title, description, source, affected_entities, indicators, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        alert.alert_type,
        alert.severity,
        alert.title,
        alert.description,
        alert.source,
        alert.affected_entities,
        alert.indicators,
        "open",
    )
    
    alert.id = row["id"]
    alert.created_at = row["created_at"]
    
    ALERTS_CREATED.labels(severity=alert.severity).inc()
    
    await event_bus.publish(
        "threats",
        Event(
            event_type=EventType.THREAT_DETECTED,
            payload={"alert_id": str(alert.id), "severity": alert.severity, "title": alert.title},
            tenant_id=tenant_id,
        )
    )
    
    logger.info("Created threat alert", extra={"alert_id": str(alert.id), "severity": alert.severity})
    return alert


@app.post("/api/v1/analyze", response_model=ThreatAnalysisResponse)
async def analyze_threat(
    request: ThreatAnalysisRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """AI-powered threat analysis using Claude."""
    ai_router = await get_ai_router()
    
    system_prompt = """You are a security threat analyst. Analyze the provided data for potential security threats.
    Return your analysis in the following JSON format:
    {
        "threat_detected": true/false,
        "severity": "low|medium|high|critical",
        "confidence": 0.0-1.0,
        "analysis": "detailed analysis",
        "recommendations": ["recommendation 1", "recommendation 2"]
    }"""
    
    user_prompt = f"Analyze this data for security threats:\n\n{request.data}"
    if request.context:
        user_prompt += f"\n\nAdditional context: {request.context}"
    
    result = await ai_router.complete(
        messages=[
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ],
        capability=ModelCapability.REASONING,
        prefer_cheap=False,
    )
    
    try:
        import json
        analysis = json.loads(result.content)
        return ThreatAnalysisResponse(**analysis)
    except:
        return ThreatAnalysisResponse(
            threat_detected=False,
            severity="low",
            confidence=0.5,
            analysis=result.content,
            recommendations=["Manual review recommended"],
        )


@app.patch("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Mark an alert as resolved."""
    db = await get_database()
    event_bus = await get_event_bus("threat-service")
    
    result = await db.execute(
        "UPDATE threat_alerts SET status = 'resolved', resolved_at = NOW() WHERE id = $1",
        alert_id,
    )
    
    await event_bus.publish(
        "threats",
        Event(
            event_type=EventType.THREAT_RESOLVED,
            payload={"alert_id": str(alert_id)},
            tenant_id=tenant_id,
        )
    )
    
    return {"status": "resolved", "alert_id": str(alert_id)}
