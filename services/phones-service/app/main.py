"""
Phones Service - Stolen/Lost Device Recovery
Device registration, loss reporting, recovery tracking
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
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from python.core_cache import get_cache
from python.core_database import get_database
from python.core_config import get_settings
from python.core_logging import setup_logging, get_logger, RequestLogger
from python.core_events import get_event_bus, Event, EventType
from python.core_spacemail import get_spacemail, EmailMessage, EmailRecipient

logger = get_logger(__name__)

DEVICES_REGISTERED = Counter("phones_devices_registered_total", "Total devices registered")
DEVICES_REPORTED = Counter("phones_devices_reported_total", "Total devices reported", ["report_type"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(level=settings.observability.log_level, format_type=settings.observability.log_format)
    logger.info("Starting Phones Service")
    
    try:
        await get_cache()
        await get_database()
    except Exception as e:
        logger.warning(f"Service dependency warning: {e}")
    
    yield
    logger.info("Shutting down Phones Service")


app = FastAPI(
    title="Phones Service - Stolen/Lost Device Recovery",
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


class Device(BaseModel):
    id: Optional[UUID] = None
    imei: str = Field(..., min_length=15, max_length=20)
    device_model: Optional[str] = None
    carrier: Optional[str] = None
    status: str = "active"
    last_known_location: Optional[dict] = None
    last_seen: Optional[datetime] = None
    reported_at: Optional[datetime] = None
    recovered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class DeviceReport(BaseModel):
    id: Optional[UUID] = None
    device_id: UUID
    report_type: str = Field(..., pattern="^(lost|stolen|found|sighting)$")
    location: Optional[dict] = None
    description: Optional[str] = None
    police_report_number: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    source: str = "gps"


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant_id


async def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_user_id


@app.get("/health/live")
async def liveness():
    return {"status": "ok", "service": "phones-service"}


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


@app.get("/api/v1/devices", response_model=List[Device])
async def list_devices(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """List registered devices."""
    db = await get_database()
    
    where_clauses = ["1=1"]
    params = []
    idx = 1
    
    if tenant_id:
        where_clauses.append(f"tenant_id = ${idx}")
        params.append(tenant_id)
        idx += 1
    if user_id:
        where_clauses.append(f"user_id = ${idx}")
        params.append(user_id)
        idx += 1
    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT id, imei, device_model, carrier, status, 
               last_known_location, last_seen, reported_at, recovered_at, created_at
        FROM registered_devices
        WHERE {" AND ".join(where_clauses)}
        ORDER BY created_at DESC
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [Device(**dict(row)) for row in rows]


@app.post("/api/v1/devices", response_model=Device, status_code=201)
async def register_device(
    device: Device,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """Register a new device."""
    db = await get_database()
    
    query = """
        INSERT INTO registered_devices 
            (tenant_id, user_id, imei, device_model, carrier, status)
        VALUES ($1, $2, $3, $4, $5, 'active')
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        user_id,
        device.imei,
        device.device_model,
        device.carrier,
    )
    
    device.id = row["id"]
    device.created_at = row["created_at"]
    device.status = "active"
    
    DEVICES_REGISTERED.inc()
    logger.info("Registered device", extra={"device_id": str(device.id), "imei": device.imei[-4:]})
    
    return device


@app.post("/api/v1/devices/{device_id}/report", response_model=DeviceReport, status_code=201)
async def report_device(
    device_id: UUID,
    report: DeviceReport,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """Report a device as lost, stolen, found, or sighted."""
    db = await get_database()
    event_bus = await get_event_bus("phones-service")
    
    report.device_id = device_id
    
    report_query = """
        INSERT INTO device_reports 
            (device_id, report_type, location, description, police_report_number, reported_by)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        report_query,
        device_id,
        report.report_type,
        report.location,
        report.description,
        report.police_report_number,
        user_id,
    )
    
    report.id = row["id"]
    report.created_at = row["created_at"]
    
    new_status = "active"
    if report.report_type == "lost":
        new_status = "lost"
    elif report.report_type == "stolen":
        new_status = "stolen"
    elif report.report_type == "found":
        new_status = "recovered"
    
    await db.execute(
        "UPDATE registered_devices SET status = $1, reported_at = NOW() WHERE id = $2",
        new_status,
        device_id,
    )
    
    DEVICES_REPORTED.labels(report_type=report.report_type).inc()
    
    await event_bus.publish(
        "devices",
        Event(
            event_type=EventType.NOTIFICATION_REQUESTED,
            payload={
                "device_id": str(device_id),
                "report_type": report.report_type,
                "report_id": str(report.id),
            },
            tenant_id=tenant_id,
        )
    )
    
    logger.info(
        "Device reported",
        extra={"device_id": str(device_id), "report_type": report.report_type}
    )
    
    return report


@app.post("/api/v1/devices/{device_id}/location")
async def update_location(
    device_id: UUID,
    location: LocationUpdate,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Update device location (for tracking lost/stolen devices)."""
    db = await get_database()
    cache = await get_cache()
    
    location_data = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "accuracy_meters": location.accuracy_meters,
        "source": location.source,
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    await db.execute(
        "UPDATE registered_devices SET last_known_location = $1, last_seen = NOW() WHERE id = $2",
        location_data,
        device_id,
    )
    
    await cache.set(f"device:location:{device_id}", location_data, ttl_sec=300)
    
    return {"status": "updated", "device_id": str(device_id)}


@app.get("/api/v1/devices/{device_id}/reports", response_model=List[DeviceReport])
async def list_device_reports(
    device_id: UUID,
    limit: int = Query(20, le=100),
):
    """List reports for a specific device."""
    db = await get_database()
    
    query = """
        SELECT id, device_id, report_type, location, description, 
               police_report_number, verified, created_at
        FROM device_reports
        WHERE device_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    """
    
    rows = await db.fetch(query, device_id, limit)
    return [DeviceReport(**dict(row)) for row in rows]


@app.get("/api/v1/search/imei/{imei}")
async def search_by_imei(
    imei: str,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Search for a device by IMEI (for checking if reported stolen)."""
    db = await get_database()
    cache = await get_cache()
    
    cache_key = f"imei:search:{imei}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    query = """
        SELECT id, status, reported_at
        FROM registered_devices
        WHERE imei = $1 AND status IN ('lost', 'stolen')
    """
    
    row = await db.fetchrow(query, imei)
    
    result = {
        "imei": imei,
        "reported": row is not None,
        "status": row["status"] if row else None,
        "reported_at": row["reported_at"].isoformat() if row and row["reported_at"] else None,
    }
    
    await cache.set(cache_key, result, ttl_sec=3600)
    
    return result
