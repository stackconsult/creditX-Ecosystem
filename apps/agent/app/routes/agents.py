"""Agent management routes."""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()

AGENT_REGISTRY = {
    "outcome_optimizer": {
        "id": "outcome_optimizer",
        "name": "Outcome Optimizer",
        "engine": "outcome",
        "description": "Optimizes credit outcomes for consumers",
        "status": "active",
        "capabilities": ["credit_analysis", "plan_generation", "goal_tracking"],
    },
    "dispute_resolution": {
        "id": "dispute_resolution",
        "name": "Dispute Resolution Agent",
        "engine": "rights_trust",
        "description": "Handles credit dispute workflows",
        "status": "active",
        "capabilities": ["dispute_filing", "evidence_analysis", "bureau_communication"],
    },
    "risk_assessor": {
        "id": "risk_assessor",
        "name": "Risk Assessment Agent",
        "engine": "risk_security",
        "description": "Assesses credit and fraud risk",
        "status": "active",
        "capabilities": ["risk_scoring", "fraud_detection", "anomaly_detection"],
    },
    "underwriting_agent": {
        "id": "underwriting_agent",
        "name": "Underwriting Agent",
        "engine": "market_capital",
        "description": "Automated underwriting decisions",
        "status": "active",
        "capabilities": ["application_review", "decision_making", "terms_generation"],
    },
    "compliance_monitor": {
        "id": "compliance_monitor",
        "name": "Compliance Monitor",
        "engine": "rights_trust",
        "description": "Monitors regulatory compliance",
        "status": "active",
        "capabilities": ["audit_logging", "policy_enforcement", "fairness_analysis"],
    },
}


class ExecuteAgentRequest(BaseModel):
    agent_id: str
    action: str
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


class ExecuteAgentResponse(BaseModel):
    execution_id: str
    agent_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    requires_hitl: bool = False
    hitl_reason: Optional[str] = None


@router.get("")
async def list_agents(
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="internal"),
):
    """List all available agents."""
    agents = list(AGENT_REGISTRY.values())
    
    if x_face == "consumer":
        agents = [a for a in agents if a["engine"] in ["outcome", "rights_trust"]]
    elif x_face == "partner":
        agents = [a for a in agents if a["engine"] in ["market_capital", "risk_security"]]
    
    return {"agents": agents, "count": len(agents)}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return AGENT_REGISTRY[agent_id]


@router.post("/execute")
async def execute_agent(
    request: ExecuteAgentRequest,
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="internal"),
):
    """Execute an agent action."""
    if request.agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
    
    execution_id = str(uuid.uuid4())
    agent = AGENT_REGISTRY[request.agent_id]
    
    requires_hitl = False
    hitl_reason = None
    
    if request.action in ["approve_loan", "delete_data", "escalate_dispute"]:
        requires_hitl = True
        hitl_reason = f"Action '{request.action}' requires human approval"
    
    result = {
        "agent": agent["name"],
        "action": request.action,
        "parameters": request.parameters,
        "output": f"Executed {request.action} successfully",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    return ExecuteAgentResponse(
        execution_id=execution_id,
        agent_id=request.agent_id,
        status="pending_hitl" if requires_hitl else "completed",
        result=result,
        requires_hitl=requires_hitl,
        hitl_reason=hitl_reason,
    )
