"""
Apps Service - 91 Apps Business Automation
Workflow automation, integrations, business process management
"""
import sys
import os
from contextlib import asynccontextmanager
from typing import Optional, List, Any
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

logger = get_logger(__name__)

WORKFLOWS_CREATED = Counter("apps_workflows_created_total", "Total workflows created")
EXECUTIONS_STARTED = Counter("apps_executions_started_total", "Total workflow executions")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(level=settings.observability.log_level, format_type=settings.observability.log_format)
    logger.info("Starting Apps Service")
    
    try:
        await get_cache()
        await get_database()
    except Exception as e:
        logger.warning(f"Service dependency warning: {e}")
    
    yield
    logger.info("Shutting down Apps Service")


app = FastAPI(
    title="Apps Service - 91 Apps Business Automation",
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


class Workflow(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: dict
    steps: List[dict]
    status: str = "active"
    run_count: int = 0
    last_run: Optional[datetime] = None
    created_at: Optional[datetime] = None


class WorkflowExecution(BaseModel):
    id: Optional[UUID] = None
    workflow_id: UUID
    status: str = "running"
    trigger_data: Optional[dict] = None
    step_results: List[dict] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TriggerRequest(BaseModel):
    trigger_data: dict = {}


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant_id


@app.get("/health/live")
async def liveness():
    return {"status": "ok", "service": "apps-service"}


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


@app.get("/api/v1/workflows", response_model=List[Workflow])
async def list_workflows(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List automation workflows."""
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
        SELECT id, name, description, trigger_type, trigger_config, steps, 
               status, run_count, last_run, created_at
        FROM automation_workflows
        WHERE {" AND ".join(where_clauses)}
        ORDER BY created_at DESC
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [Workflow(**dict(row)) for row in rows]


@app.post("/api/v1/workflows", response_model=Workflow, status_code=201)
async def create_workflow(
    workflow: Workflow,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Create a new automation workflow."""
    db = await get_database()
    
    query = """
        INSERT INTO automation_workflows 
            (tenant_id, name, description, trigger_type, trigger_config, steps, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        workflow.name,
        workflow.description,
        workflow.trigger_type,
        workflow.trigger_config,
        workflow.steps,
        "active",
    )
    
    workflow.id = row["id"]
    workflow.created_at = row["created_at"]
    
    WORKFLOWS_CREATED.inc()
    logger.info("Created workflow", extra={"workflow_id": str(workflow.id), "name": workflow.name})
    
    return workflow


@app.post("/api/v1/workflows/{workflow_id}/trigger", response_model=WorkflowExecution)
async def trigger_workflow(
    workflow_id: UUID,
    request: TriggerRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Manually trigger a workflow execution."""
    db = await get_database()
    event_bus = await get_event_bus("apps-service")
    
    workflow = await db.fetchrow(
        "SELECT id, steps FROM automation_workflows WHERE id = $1",
        workflow_id,
    )
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    exec_query = """
        INSERT INTO automation_executions (workflow_id, status, trigger_data, started_at)
        VALUES ($1, 'running', $2, NOW())
        RETURNING id, started_at
    """
    
    row = await db.fetchrow(exec_query, workflow_id, request.trigger_data)
    
    execution = WorkflowExecution(
        id=row["id"],
        workflow_id=workflow_id,
        status="running",
        trigger_data=request.trigger_data,
        started_at=row["started_at"],
    )
    
    await db.execute(
        "UPDATE automation_workflows SET run_count = run_count + 1, last_run = NOW() WHERE id = $1",
        workflow_id,
    )
    
    EXECUTIONS_STARTED.inc()
    
    await event_bus.publish(
        "workflows",
        Event(
            event_type=EventType.WORKFLOW_STARTED,
            payload={"execution_id": str(execution.id), "workflow_id": str(workflow_id)},
            tenant_id=tenant_id,
        )
    )
    
    logger.info("Triggered workflow", extra={"workflow_id": str(workflow_id), "execution_id": str(execution.id)})
    
    return execution


@app.get("/api/v1/workflows/{workflow_id}/executions", response_model=List[WorkflowExecution])
async def list_executions(
    workflow_id: UUID,
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List workflow executions."""
    db = await get_database()
    
    where_clauses = [f"workflow_id = $1"]
    params = [workflow_id]
    idx = 2
    
    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1
    
    params.append(limit)
    
    query = f"""
        SELECT id, workflow_id, status, trigger_data, step_results, 
               error_message, started_at, completed_at
        FROM automation_executions
        WHERE {" AND ".join(where_clauses)}
        ORDER BY started_at DESC
        LIMIT ${idx}
    """
    
    rows = await db.fetch(query, *params)
    return [WorkflowExecution(**dict(row)) for row in rows]


@app.patch("/api/v1/workflows/{workflow_id}")
async def update_workflow_status(
    workflow_id: UUID,
    status: str = Query(..., pattern="^(active|paused|disabled)$"),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Update workflow status."""
    db = await get_database()
    
    await db.execute(
        "UPDATE automation_workflows SET status = $1, updated_at = NOW() WHERE id = $2",
        status,
        workflow_id,
    )
    
    return {"status": status, "workflow_id": str(workflow_id)}
