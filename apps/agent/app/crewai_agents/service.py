"""CrewAI agent service layer."""
import asyncio
from typing import Dict, Any, Optional, List
import structlog
from crewai import Crew
from crewai.flow import Flow
from copilotkit.crewai import CrewAIAgent, copilotkit_predict_state, copilotkit_emit_message, copilotkit_emit_tool_call

from .config import AGENT_REGISTRY

logger = structlog.get_logger()

class CrewAIService:
    """Service for managing CrewAI agents and CopilotKit integration."""
    
    def __init__(self):
        self.crewai_agents: Dict[str, CrewAIAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize CrewAI agents for CopilotKit."""
        try:
            # Register credit optimizer agent
            self.crewai_agents["credit_optimizer"] = CrewAIAgent(
                name="credit_optimizer",
                description="Optimizes credit scores through analysis and recommendations",
                crew=AGENT_REGISTRY["credit_optimizer"]["crew"],
            )
            
            # Register dispute handler agent
            self.crewai_agents["dispute_handler"] = CrewAIAgent(
                name="dispute_handler",
                description="Handles credit disputes with bureaus",
                crew=AGENT_REGISTRY["dispute_handler"]["crew"],
            )
            
            # Register risk assessor agent
            self.crewai_agents["risk_assessor"] = CrewAIAgent(
                name="risk_assessor",
                description="Assesses credit and fraud risk",
                crew=AGENT_REGISTRY["risk_assessor"]["crew"],
            )
            
            # Register underwriter agent
            self.crewai_agents["underwriter"] = CrewAIAgent(
                name="underwriter",
                description="Performs automated underwriting",
                crew=AGENT_REGISTRY["underwriter"]["crew"],
            )
            
            # Register credit optimizer flow
            self.crewai_agents["credit_optimizer_flow"] = CrewAIAgent(
                name="credit_optimizer_flow",
                description="Flow-based credit optimization process",
                flow=AGENT_REGISTRY["credit_optimizer"]["flow"],
            )
            
            logger.info("CrewAI agents initialized successfully", count=len(self.crewai_agents))
            
        except Exception as e:
            logger.error("Failed to initialize CrewAI agents", error=str(e))
            raise
    
    async def execute_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Execute a CrewAI agent with CopilotKit integration."""
        try:
            if agent_name not in self.crewai_agents:
                raise ValueError(f"Agent {agent_name} not found")
            
            agent = self.crewai_agents[agent_name]
            
            # Emit initial state
            await copilotkit_predict_state({
                "status": "starting",
                "agent": agent_name,
                "tenant": tenant_id,
                "progress": 0,
            })
            
            # Execute the agent
            logger.info("Executing CrewAI agent", agent=agent_name, tenant=tenant_id)
            
            # For flow-based agents
            if hasattr(agent, 'flow') and agent.flow:
                result = await self._execute_flow(agent.flow, input_data, agent_name)
            # For crew-based agents
            elif hasattr(agent, 'crew') and agent.crew:
                result = await self._execute_crew(agent.crew, input_data, agent_name)
            else:
                raise ValueError(f"Agent {agent_name} has no crew or flow configured")
            
            # Emit completion state
            await copilotkit_predict_state({
                "status": "completed",
                "agent": agent_name,
                "tenant": tenant_id,
                "progress": 100,
                "result": result,
            })
            
            return {
                "success": True,
                "agent": agent_name,
                "result": result,
                "tenant_id": tenant_id,
            }
            
        except Exception as e:
            logger.error("Agent execution failed", agent=agent_name, error=str(e))
            
            # Emit error state
            await copilotkit_predict_state({
                "status": "error",
                "agent": agent_name,
                "tenant": tenant_id,
                "error": str(e),
            })
            
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e),
                "tenant_id": tenant_id,
            }
    
    async def _execute_crew(
        self,
        crew: Crew,
        input_data: Dict[str, Any],
        agent_name: str,
    ) -> Dict[str, Any]:
        """Execute a CrewAI crew with streaming."""
        try:
            # Update tasks with input data
            for task in crew.tasks:
                if hasattr(task, 'description'):
                    # Replace placeholders in task description
                    for key, value in input_data.items():
                        if isinstance(value, str):
                            task.description = task.description.replace(f"{{{key}}}", str(value))
            
            # Emit progress message
            await copilotkit_emit_message(f"Starting {agent_name} crew execution...")
            
            # Execute crew in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, crew.kickoff)
            
            # Emit completion message
            await copilotkit_emit_message(f"{agent_name} crew execution completed")
            
            return {
                "type": "crew_result",
                "output": str(result),
                "tasks_completed": len(crew.tasks),
            }
            
        except Exception as e:
            logger.error("Crew execution failed", agent=agent_name, error=str(e))
            raise
    
    async def _execute_flow(
        self,
        flow: Flow,
        input_data: Dict[str, Any],
        agent_name: str,
    ) -> Dict[str, Any]:
        """Execute a CrewAI flow with streaming."""
        try:
            # Emit progress message
            await copilotkit_emit_message(f"Starting {agent_name} flow execution...")
            
            # Execute flow steps
            flow_result = {}
            
            # Start the flow
            start_result = flow.analyze_credit()
            flow_result.update(start_result)
            await copilotkit_predict_state({
                "flow_step": "analyze_credit",
                "status": start_result.get("status"),
                "progress": 25,
            })
            await copilotkit_emit_message("Credit analysis completed")
            
            # Generate recommendations
            rec_result = flow.generate_recommendations()
            flow_result.update(rec_result)
            await copilotkit_predict_state({
                "flow_step": "generate_recommendations",
                "status": rec_result.get("status"),
                "progress": 50,
            })
            await copilotkit_emit_message("Recommendations generated")
            
            # Compliance check
            compliance_result = flow.compliance_check()
            flow_result.update(compliance_result)
            await copilotkit_predict_state({
                "flow_step": "compliance_check",
                "status": compliance_result.get("status"),
                "progress": 75,
            })
            await copilotkit_emit_message("Compliance check completed")
            
            # Finalize
            final_result = flow.finalize_report()
            flow_result.update(final_result)
            await copilotkit_predict_state({
                "flow_step": "finalize_report",
                "status": final_result.get("status"),
                "progress": 100,
            })
            await copilotkit_emit_message(f"{agent_name} flow execution completed")
            
            return {
                "type": "flow_result",
                "steps": flow_result,
                "final_status": final_result.get("status"),
            }
            
        except Exception as e:
            logger.error("Flow execution failed", agent=agent_name, error=str(e))
            raise
    
    async def emit_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
    ) -> None:
        """Emit a tool call to CopilotKit."""
        try:
            await copilotkit_emit_tool_call(name=tool_name, args=tool_args)
            logger.info("Tool call emitted", tool=tool_name, args=tool_args)
        except Exception as e:
            logger.error("Failed to emit tool call", tool=tool_name, error=str(e))
    
    async def emit_message(self, message: str) -> None:
        """Emit a message to CopilotKit."""
        try:
            await copilotkit_emit_message(message)
            logger.info("Message emitted", message=message)
        except Exception as e:
            logger.error("Failed to emit message", message=message, error=str(e))
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available CrewAI agents."""
        agents = []
        for name, agent in self.crewai_agents.items():
            agents.append({
                "name": name,
                "description": agent.description,
                "type": "flow" if hasattr(agent, 'flow') and agent.flow else "crew",
            })
        return agents
    
    def get_agent(self, agent_name: str) -> Optional[CrewAIAgent]:
        """Get a specific CrewAI agent."""
        return self.crewai_agents.get(agent_name)

# Global service instance
crewai_service = CrewAIService()
