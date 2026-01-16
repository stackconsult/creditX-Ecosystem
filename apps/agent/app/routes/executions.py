"""Execution tracking routes."""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter()

EXECUTIONS_STORE: Dict[str, Dict] = {}


class ExecutionStatus(BaseModel):
    execution_id: str
    agent_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("")
async def list_executions(
    limit: int = 50,
    status: Optional[str] = None,
    x_tenant_id: str = Header(default="default"),
):
    """List recent executions."""
    executions = list(EXECUTIONS_STORE.values())
    
    if status:
        executions = [e for e in executions if e["status"] == status]
    
    executions = sorted(executions, key=lambda x: x["started_at"], reverse=True)[:limit]
    
    return {"executions": executions, "count": len(executions)}


@router.get("/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution details."""
    if execution_id not in EXECUTIONS_STORE:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    return EXECUTIONS_STORE[execution_id]


@router.post("/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel a running execution."""
    if execution_id not in EXECUTIONS_STORE:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    execution = EXECUTIONS_STORE[execution_id]
    if execution["status"] not in ["running", "pending"]:
        raise HTTPException(status_code=400, detail="Execution cannot be cancelled")
    
    execution["status"] = "cancelled"
    execution["completed_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Execution cancelled", "execution_id": execution_id}
