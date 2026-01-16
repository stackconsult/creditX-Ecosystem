"""
CopilotKit Agent Routes - Enterprise Agent API
Agent execution, HITL approval, and face-based routing
"""
import sys
import os
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from python.core_agents import (
    get_orchestrator,
    Face,
    AgentConfig,
    AgentState,
)
from python.core_logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent."""
    agent_id: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentExecuteResponse(BaseModel):
    """Response from agent execution."""
    task_id: str
    agent_id: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    hitl_required: bool = False
    hitl_approved: Optional[bool] = None


class HITLApprovalRequest(BaseModel):
    """Request to approve/reject HITL."""
    task_id: str
    approved: bool
    response: Optional[str] = None


class AgentListResponse(BaseModel):
    """List of available agents."""
    agents: List[Dict[str, Any]]
    face: str
    count: int


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_tenant_id


async def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_user_id


async def get_face(x_face: Optional[str] = Header(None)) -> Face:
    """Get user's OS face from header."""
    if x_face:
        try:
            return Face(x_face.lower())
        except ValueError:
            pass
    return Face.INTERNAL


@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    face: Face = Depends(get_face),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    List agents available to the current user's face.
    Consumer OS users see consumer-facing agents.
    Partner OS users see partner-facing agents.
    Internal OS users see all internal agents.
    """
    orchestrator = await get_orchestrator()
    agents = orchestrator.get_available_agents(face)
    
    return AgentListResponse(
        agents=[
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "engine": a.engine.value,
                "agent_type": a.agent_type.value,
                "risk_level": a.risk_level.value,
                "requires_hitl": a.requires_hitl(),
            }
            for a in agents
        ],
        face=face.value,
        count=len(agents),
    )


@router.post("/agents/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    request: AgentExecuteRequest,
    face: Face = Depends(get_face),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """
    Execute an agent task.
    
    For high-risk agents, execution will pause at HITL gate
    and require approval before completing.
    """
    orchestrator = await get_orchestrator()
    
    state = await orchestrator.execute(
        agent_id=request.agent_id,
        input_data=request.input_data,
        tenant_id=tenant_id,
        user_id=user_id,
        face=face,
        context=request.context,
    )
    
    logger.info(
        "Agent executed",
        extra={
            "task_id": state.get("task_id"),
            "agent_id": request.agent_id,
            "status": state.get("status"),
            "face": face.value,
        }
    )
    
    return AgentExecuteResponse(
        task_id=state.get("task_id", ""),
        agent_id=request.agent_id,
        status=state.get("status", "unknown"),
        output=state.get("output"),
        error=state.get("error"),
        hitl_required=state.get("hitl_required", False),
        hitl_approved=state.get("hitl_approved"),
    )


@router.post("/agents/hitl/approve")
async def approve_hitl(
    request: HITLApprovalRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """
    Approve or reject a pending HITL request.
    Only available to Internal OS users with appropriate permissions.
    """
    orchestrator = await get_orchestrator()
    
    success = await orchestrator.approve_hitl(
        task_id=request.task_id,
        approved=request.approved,
        response=request.response,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="HITL task not found or expired")
    
    logger.info(
        "HITL decision made",
        extra={
            "task_id": request.task_id,
            "approved": request.approved,
            "user_id": user_id,
        }
    )
    
    return {
        "task_id": request.task_id,
        "approved": request.approved,
        "status": "processed",
    }


@router.post("/copilotkit")
async def copilotkit_handler(
    request: Dict[str, Any],
    face: Face = Depends(get_face),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """
    CopilotKit integration endpoint.
    Routes CopilotKit actions to appropriate agents.
    
    Supports AG-UI Protocol for shared state and generative UI.
    """
    action = request.get("action", "")
    module = request.get("module", "")
    parameters = request.get("parameters", {})
    
    agent_mapping = {
        "creditx": {
            "analyze_document": "outcome.plan_generation.v1",
            "check_compliance": "rights_trust.audit_compliance.v1",
            "explain": "cross.explainer.v1",
        },
        "91-apps": {
            "create_workflow": "outcome.campaign_tuning.v1",
            "explain": "cross.explainer.v1",
        },
        "global-ai-alert": {
            "analyze_threat": "risk_security.threat_intel.v1",
            "aggregate_alerts": "risk_security.alert_aggregator.v1",
            "explain": "cross.explainer.v1",
        },
        "guardian-ai": {
            "remediate": "risk_security.remediation.v1",
            "explain": "cross.explainer.v1",
        },
        "stolen-phones": {
            "notify": "cross.notification.v1",
            "explain": "cross.explainer.v1",
        },
    }
    
    module_agents = agent_mapping.get(module, {})
    agent_id = module_agents.get(action, "cross.explainer.v1")
    
    orchestrator = await get_orchestrator()
    
    state = await orchestrator.execute(
        agent_id=agent_id,
        input_data=parameters,
        tenant_id=tenant_id,
        user_id=user_id,
        face=face,
        context={"module": module, "action": action},
    )
    
    return {
        "success": state.get("status") == "completed",
        "task_id": state.get("task_id"),
        "result": state.get("output"),
        "error": state.get("error"),
        "hitl_required": state.get("hitl_required", False),
    }
