"""Chat routes for CopilotKit integration."""
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.services.llm import LLMService

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict[str, Any]] = None
    agent_id: Optional[str] = None


class ChatResponse(BaseModel):
    id: str
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None


SYSTEM_PROMPTS = {
    "consumer": """You are CreditX Assistant, helping consumers understand and improve their credit.
You have access to their credit report, disputes, and improvement plans.
Be helpful, clear, and always protect consumer rights.
Never share sensitive information without verification.""",

    "partner": """You are CreditX Partner Assistant, helping lenders manage their portfolio.
You can assist with underwriting decisions, risk analysis, and compliance.
Always ensure fair lending practices and regulatory compliance.""",

    "internal": """You are CreditX Internal Assistant for system operators.
You can help with agent management, HITL approvals, and system monitoring.
Provide technical details and operational insights.""",
}


@router.post("")
async def chat(
    request: ChatRequest,
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="consumer"),
):
    """Process a chat message."""
    try:
        llm_service = LLMService()
        
        system_prompt = SYSTEM_PROMPTS.get(x_face, SYSTEM_PROMPTS["consumer"])
        
        if request.context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in request.context.items()])
            system_prompt += f"\n\nCurrent context:\n{context_str}"
        
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response_content = await llm_service.chat(messages, system_prompt)
        
        return ChatResponse(
            id=str(uuid.uuid4()),
            message=ChatMessage(role="assistant", content=response_content),
            usage={"prompt_tokens": 0, "completion_tokens": 0},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilotkit")
async def copilotkit_handler(
    request: Request,
    x_tenant_id: str = Header(default="default"),
    x_face: str = Header(default="consumer"),
):
    """CopilotKit compatible endpoint."""
    body = await request.json()
    
    messages = body.get("messages", [])
    
    chat_request = ChatRequest(
        messages=[ChatMessage(role=m["role"], content=m["content"]) for m in messages],
        context=body.get("context"),
    )
    
    return await chat(chat_request, x_tenant_id, x_face)
