"""CopilotKit integration routes for CrewAI agents."""
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import structlog
from sse_starlette.sse import EventSourceResponse

from ..crewai_agents.service import crewai_service

logger = structlog.get_logger()
router = APIRouter()

class CopilotKitRequest(BaseModel):
    """Request model for CopilotKit integration."""
    agent_name: str
    input_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class CopilotKitResponse(BaseModel):
    """Response model for CopilotKit integration."""
    success: bool
    agent_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

@router.post("/execute")
async def execute_crewai_agent(
    request: CopilotKitRequest,
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="internal"),
):
    """Execute a CrewAI agent via CopilotKit."""
    try:
        logger.info(
            "CopilotKit agent execution request",
            agent=request.agent_name,
            tenant=x_tenant_id,
            face=x_face,
        )
        
        # Execute the agent
        result = await crewai_service.execute_agent(
            agent_name=request.agent_name,
            input_data=request.input_data,
            tenant_id=x_tenant_id,
        )
        
        # Add metadata
        result["metadata"] = {
            "face": x_face,
            "request_metadata": request.metadata,
        }
        
        return CopilotKitResponse(**result)
        
    except Exception as e:
        logger.error(
            "CopilotKit agent execution failed",
            agent=request.agent_name,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}",
        )

@router.get("/agents")
async def list_crewai_agents(
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="internal"),
):
    """List all available CrewAI agents for CopilotKit."""
    try:
        agents = crewai_service.list_agents()
        
        # Filter agents based on face
        if x_face == "consumer":
            agents = [a for a in agents if a["name"] in ["credit_optimizer", "dispute_handler"]]
        elif x_face == "partner":
            agents = [a for a in agents if a["name"] in ["risk_assessor", "underwriter"]]
        
        return {
            "agents": agents,
            "count": len(agents),
            "tenant_id": x_tenant_id,
            "face": x_face,
        }
        
    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}",
        )

@router.get("/agents/{agent_name}")
async def get_crewai_agent(
    agent_name: str,
    x_tenant_id: str = Header(default="default"),
):
    """Get details of a specific CrewAI agent."""
    try:
        agent = crewai_service.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_name} not found",
            )
        
        return {
            "name": agent.name,
            "description": agent.description,
            "type": "flow" if hasattr(agent, 'flow') and agent.flow else "crew",
            "tenant_id": x_tenant_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent=agent_name, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent: {str(e)}",
        )

@router.post("/stream")
async def stream_crewai_agent(
    request: CopilotKitRequest,
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="internal"),
):
    """Stream CrewAI agent execution with SSE."""
    async def generate_events():
        try:
            logger.info(
                "Starting CrewAI agent stream",
                agent=request.agent_name,
                tenant=x_tenant_id,
            )
            
            # Send initial event
            yield {
                "event": "start",
                "data": json.dumps({
                    "status": "starting",
                    "agent": request.agent_name,
                    "tenant_id": x_tenant_id,
                }),
            }
            
            # Execute agent and stream results
            # Note: In a real implementation, you'd need to modify the service
            # to support streaming with yield statements
            result = await crewai_service.execute_agent(
                agent_name=request.agent_name,
                input_data=request.input_data,
                tenant_id=x_tenant_id,
            )
            
            # Send progress events
            yield {
                "event": "progress",
                "data": json.dumps({
                    "status": "progress",
                    "progress": 50,
                    "message": "Processing...",
                }),
            }
            
            # Send completion event
            yield {
                "event": "complete",
                "data": json.dumps(result),
            }
            
        except Exception as e:
            logger.error("Stream error", error=str(e))
            yield {
                "event": "error",
                "data": json.dumps({
                    "status": "error",
                    "error": str(e),
                }),
            }
    
    return EventSourceResponse(generate_events())

@router.post("/tools/{tool_name}")
async def emit_tool_call(
    tool_name: str,
    tool_args: Dict[str, Any],
    x_tenant_id: str = Header(default="default"),
):
    """Emit a tool call to CopilotKit."""
    try:
        await crewai_service.emit_tool_call(tool_name, tool_args)
        
        return {
            "success": True,
            "tool": tool_name,
            "args": tool_args,
            "tenant_id": x_tenant_id,
        }
        
    except Exception as e:
        logger.error("Failed to emit tool call", tool=tool_name, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to emit tool call: {str(e)}",
        )

@router.post("/message")
async def emit_message(
    message: str,
    x_tenant_id: str = Header(default="default"),
):
    """Emit a message to CopilotKit."""
    try:
        await crewai_service.emit_message(message)
        
        return {
            "success": True,
            "message": message,
            "tenant_id": x_tenant_id,
        }
        
    except Exception as e:
        logger.error("Failed to emit message", message=message, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to emit message: {str(e)}",
        )
