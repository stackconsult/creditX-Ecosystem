"""
Enterprise Agent Orchestration Framework
- LangGraph-based agent workflows
- HITL (Human-in-the-Loop) gates for risk-tiered approval
- Face-based agent visibility (Consumer, Partner, Internal)
- CopilotKit integration ready
- Agent registry and routing
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List, Callable, TypedDict, Annotated
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import uuid

from .core_ai import get_ai_router, Message, ModelCapability
from .core_events import get_event_bus, Event, EventType
from .core_database import get_database
from .core_cache import get_cache

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Agent classification by authority level."""
    ASSISTANT = "assistant"
    OPERATOR = "operator"
    AMBASSADOR = "ambassador"


class RiskLevel(str, Enum):
    """Risk level determining HITL requirements."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Face(str, Enum):
    """OS face determining agent visibility."""
    CONSUMER = "consumer"
    PARTNER = "partner"
    INTERNAL = "internal"


class Engine(str, Enum):
    """Agent engine/domain classification."""
    OUTCOME = "outcome"
    RIGHTS_TRUST = "rights_trust"
    RISK_SECURITY = "risk_security"
    MARKET_CAPITAL = "market_capital"
    CROSS = "cross"


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    VALIDATING = "validating"
    EXECUTING = "executing"
    WAITING_HITL = "waiting_hitl"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentConfig:
    """Agent configuration from registry."""
    agent_id: str
    name: str
    engine: Engine
    agent_type: AgentType
    faces: List[Face]
    risk_level: RiskLevel
    status: str = "active"
    version: str = "1.0.0"
    config: Dict[str, Any] = field(default_factory=dict)
    
    def is_visible_to(self, face: Face) -> bool:
        """Check if agent is visible to a face."""
        return face in self.faces
    
    def requires_hitl(self) -> bool:
        """Check if agent requires human approval."""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


class AgentState(TypedDict, total=False):
    """State passed through agent workflow."""
    task_id: str
    agent_id: str
    tenant_id: Optional[str]
    user_id: Optional[str]
    face: str
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    messages: List[Dict[str, str]]
    output: Optional[Dict[str, Any]]
    status: str
    error: Optional[str]
    hitl_required: bool
    hitl_approved: Optional[bool]
    hitl_response: Optional[str]
    started_at: str
    completed_at: Optional[str]


@dataclass
class AgentTask:
    """Represents an agent execution task."""
    task_id: str
    agent_id: str
    tenant_id: Optional[str]
    user_id: Optional[str]
    face: Face
    input_data: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_state(self) -> AgentState:
        """Convert to workflow state."""
        return AgentState(
            task_id=self.task_id,
            agent_id=self.agent_id,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            face=self.face.value,
            input_data=self.input_data,
            context=self.context,
            messages=[],
            output=None,
            status=self.status.value,
            error=None,
            hitl_required=False,
            hitl_approved=None,
            hitl_response=None,
            started_at=datetime.utcnow().isoformat(),
            completed_at=None,
        )


class BaseAgent(ABC):
    """
    Base class for all CreditX agents.
    Implements standard workflow with HITL support.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.ai_router = None
        self.event_bus = None
        self.db = None
        self.cache = None
    
    async def _init_dependencies(self):
        """Initialize async dependencies."""
        if self.ai_router is None:
            self.ai_router = await get_ai_router()
        if self.event_bus is None:
            self.event_bus = await get_event_bus(f"agent-{self.config.agent_id}")
        if self.db is None:
            self.db = await get_database()
        if self.cache is None:
            self.cache = await get_cache()
    
    @abstractmethod
    async def validate_input(self, state: AgentState) -> AgentState:
        """Validate input data. Must be implemented by subclass."""
        pass
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute main agent logic. Must be implemented by subclass."""
        pass
    
    async def check_hitl(self, state: AgentState) -> AgentState:
        """Check if HITL approval is required."""
        if self.config.requires_hitl():
            state["hitl_required"] = True
            state["status"] = AgentStatus.WAITING_HITL.value
            
            await self.event_bus.publish(
                "agent-hitl",
                Event(
                    event_type=EventType.NOTIFICATION_REQUESTED,
                    payload={
                        "task_id": state["task_id"],
                        "agent_id": self.config.agent_id,
                        "agent_name": self.config.name,
                        "risk_level": self.config.risk_level.value,
                        "input_summary": str(state["input_data"])[:500],
                    },
                    tenant_id=state.get("tenant_id"),
                )
            )
            
            logger.info(
                "HITL approval required",
                extra={"task_id": state["task_id"], "agent_id": self.config.agent_id}
            )
        else:
            state["hitl_required"] = False
            state["hitl_approved"] = True
        
        return state
    
    async def finalize(self, state: AgentState) -> AgentState:
        """Finalize agent execution."""
        state["completed_at"] = datetime.utcnow().isoformat()
        
        if state.get("error"):
            state["status"] = AgentStatus.FAILED.value
        else:
            state["status"] = AgentStatus.COMPLETED.value
        
        await self.event_bus.publish(
            "agent-tasks",
            Event(
                event_type=EventType.AGENT_TASK_COMPLETED if not state.get("error") else EventType.AGENT_TASK_FAILED,
                payload={
                    "task_id": state["task_id"],
                    "agent_id": self.config.agent_id,
                    "status": state["status"],
                    "has_output": state.get("output") is not None,
                },
                tenant_id=state.get("tenant_id"),
            )
        )
        
        return state
    
    async def run(self, task: AgentTask) -> AgentState:
        """
        Execute the full agent workflow.
        Validate -> Check HITL -> Execute -> Finalize
        """
        await self._init_dependencies()
        
        state = task.to_state()
        state["status"] = AgentStatus.VALIDATING.value
        
        try:
            state = await self.validate_input(state)
            
            if state.get("error"):
                return await self.finalize(state)
            
            state = await self.check_hitl(state)
            
            if state["hitl_required"] and not state.get("hitl_approved"):
                return state
            
            state["status"] = AgentStatus.EXECUTING.value
            state = await self.execute(state)
            
            return await self.finalize(state)
        
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            state["error"] = str(e)
            state["status"] = AgentStatus.FAILED.value
            return await self.finalize(state)
    
    async def complete_with_ai(
        self,
        prompt: str,
        system: Optional[str] = None,
        capability: ModelCapability = ModelCapability.REASONING,
    ) -> str:
        """Helper to get AI completion."""
        messages = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=prompt))
        
        result = await self.ai_router.complete(
            messages=messages,
            capability=capability,
        )
        return result.content


class ExplainerAgent(BaseAgent):
    """Cross-cutting agent that explains decisions to all faces."""
    
    async def validate_input(self, state: AgentState) -> AgentState:
        if "decision_id" not in state["input_data"] and "topic" not in state["input_data"]:
            state["error"] = "Either decision_id or topic is required"
        return state
    
    async def execute(self, state: AgentState) -> AgentState:
        topic = state["input_data"].get("topic", "the decision")
        decision_id = state["input_data"].get("decision_id")
        
        system_prompt = """You are an Explainer Agent for CreditX. Your role is to explain 
        complex financial and compliance decisions in clear, simple language appropriate 
        for the user's role. Be concise, accurate, and helpful."""
        
        user_prompt = f"Explain {topic} in simple terms."
        if decision_id:
            user_prompt = f"Explain the decision with ID {decision_id} and why it was made."
        
        explanation = await self.complete_with_ai(
            prompt=user_prompt,
            system=system_prompt,
            capability=ModelCapability.REASONING,
        )
        
        state["output"] = {
            "explanation": explanation,
            "topic": topic,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        return state


class NotificationAgent(BaseAgent):
    """Cross-cutting agent that sends notifications across all faces."""
    
    async def validate_input(self, state: AgentState) -> AgentState:
        required = ["recipient", "message_type"]
        for field in required:
            if field not in state["input_data"]:
                state["error"] = f"Missing required field: {field}"
                return state
        return state
    
    async def execute(self, state: AgentState) -> AgentState:
        from .core_spacemail import get_spacemail, EmailMessage, EmailRecipient
        
        recipient = state["input_data"]["recipient"]
        message_type = state["input_data"]["message_type"]
        subject = state["input_data"].get("subject", "CreditX Notification")
        body = state["input_data"].get("body", "")
        
        if not body:
            system_prompt = "Generate a professional notification email body."
            body = await self.complete_with_ai(
                prompt=f"Write a notification about: {message_type}",
                system=system_prompt,
                capability=ModelCapability.FAST_INFERENCE,
            )
        
        try:
            spacemail = await get_spacemail()
            result = await spacemail.send(EmailMessage(
                to=[EmailRecipient(email=recipient)],
                subject=subject,
                text_body=body,
            ))
            
            state["output"] = {
                "sent": True,
                "message_id": result.message_id,
                "recipient": recipient,
            }
        except Exception as e:
            state["output"] = {
                "sent": False,
                "error": str(e),
                "recipient": recipient,
            }
        
        return state


AGENT_REGISTRY: Dict[str, type] = {
    "cross.explainer.v1": ExplainerAgent,
    "cross.notification.v1": NotificationAgent,
}


class AgentOrchestrator:
    """
    Central orchestrator for agent execution.
    Handles routing, face visibility, and HITL coordination.
    """
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._configs: Dict[str, AgentConfig] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Load agent configurations from database."""
        if self._initialized:
            return
        
        try:
            db = await get_database()
            rows = await db.fetch("""
                SELECT agent_id, name, engine, agent_type, faces, risk_level, status, config, version
                FROM agent_registry
                WHERE status = 'active'
            """)
            
            for row in rows:
                config = AgentConfig(
                    agent_id=row["agent_id"],
                    name=row["name"],
                    engine=Engine(row["engine"]),
                    agent_type=AgentType(row["agent_type"]),
                    faces=[Face(f) for f in row["faces"]],
                    risk_level=RiskLevel(row["risk_level"]),
                    status=row["status"],
                    config=row["config"] or {},
                    version=row["version"],
                )
                self._configs[config.agent_id] = config
                
                agent_class = AGENT_REGISTRY.get(config.agent_id)
                if agent_class:
                    self._agents[config.agent_id] = agent_class(config)
            
            self._initialized = True
            logger.info(f"Loaded {len(self._configs)} agent configurations")
        
        except Exception as e:
            logger.warning(f"Could not load agents from database: {e}")
            self._initialized = True
    
    def get_available_agents(self, face: Face) -> List[AgentConfig]:
        """Get agents visible to a specific face."""
        return [
            config for config in self._configs.values()
            if config.is_visible_to(face) and config.status == "active"
        ]
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent instance by ID."""
        return self._agents.get(agent_id)
    
    async def execute(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        face: Face = Face.INTERNAL,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentState:
        """Execute an agent task."""
        await self.initialize()
        
        agent = self.get_agent(agent_id)
        if not agent:
            return AgentState(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                status=AgentStatus.FAILED.value,
                error=f"Agent not found: {agent_id}",
                started_at=datetime.utcnow().isoformat(),
            )
        
        config = self._configs.get(agent_id)
        if config and not config.is_visible_to(face):
            return AgentState(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                status=AgentStatus.FAILED.value,
                error=f"Agent not accessible from {face.value} face",
                started_at=datetime.utcnow().isoformat(),
            )
        
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_id=agent_id,
            tenant_id=tenant_id,
            user_id=user_id,
            face=face,
            input_data=input_data,
            context=context or {},
        )
        
        return await agent.run(task)
    
    async def approve_hitl(
        self,
        task_id: str,
        approved: bool,
        response: Optional[str] = None,
    ) -> bool:
        """Approve or reject a pending HITL request."""
        cache = await get_cache()
        
        task_data = await cache.get(f"hitl:{task_id}")
        if not task_data:
            return False
        
        task_data["hitl_approved"] = approved
        task_data["hitl_response"] = response
        
        await cache.set(f"hitl:{task_id}", task_data, ttl_sec=3600)
        
        event_bus = await get_event_bus("orchestrator")
        await event_bus.publish(
            "agent-hitl-response",
            Event(
                event_type=EventType.AGENT_TASK_COMPLETED,
                payload={
                    "task_id": task_id,
                    "approved": approved,
                    "response": response,
                },
            )
        )
        
        return True


_orchestrator_instance: Optional[AgentOrchestrator] = None


async def get_orchestrator() -> AgentOrchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()
        await _orchestrator_instance.initialize()
    return _orchestrator_instance
