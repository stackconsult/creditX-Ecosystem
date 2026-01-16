"""
Cross-Cutting Agents (2 agents)
Purpose: Serve all faces and engines with explanation and notification capabilities
"""
from typing import Dict, Any, List, Optional
import logging

from ..core_agents import BaseAgent, AgentConfig, AgentType, Engine, RiskLevel, Face

logger = logging.getLogger(__name__)


class ExplainerAgent(BaseAgent):
    """
    Agent 19: Explainer Agent
    Generate plain-language explanations for any agent decision or system state.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="cross.explainer.v1",
            name="Explainer Agent",
            engine=Engine.CROSS_CUTTING,
            agent_type=AgentType.ASSISTANT,
            risk_level=RiskLevel.LOW,
            faces=[Face.CONSUMER, Face.PARTNER, Face.INTERNAL],
            scope="Generate plain-language explanations for decisions and states",
            input_entities=["DecisionContext", "SystemState", "UserProfile"],
            output_entities=["Explanation", "VisualizationData", "ActionSuggestions"],
            required_tools=["get_decision_context", "generate_explanation", "create_visualization"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic", "")
        decision_id = input_data.get("decision_id")
        audience = input_data.get("audience", "consumer")
        detail_level = input_data.get("detail_level", "summary")
        
        # Get context
        decision_context = await self._get_decision_context(decision_id)
        
        # Generate explanation
        explanation = self._generate_explanation(topic, decision_context, audience, detail_level)
        
        # Create visualization data
        viz = self._create_visualization(decision_context)
        
        # Suggest actions
        actions = self._suggest_actions(decision_context, audience)
        
        return {
            "status": "completed",
            "topic": topic,
            "explanation": explanation,
            "visualization": viz,
            "suggested_actions": actions,
        }
    
    async def _get_decision_context(self, decision_id: str) -> Dict[str, Any]:
        return {
            "decision_type": "underwriting",
            "result": "approved",
            "factors": [
                {"name": "credit_score", "impact": "positive", "weight": 0.4},
                {"name": "income", "impact": "positive", "weight": 0.3},
                {"name": "debt_ratio", "impact": "neutral", "weight": 0.3},
            ],
        }
    
    def _generate_explanation(self, topic: str, context: Dict, audience: str, detail: str) -> str:
        if audience == "consumer":
            return self._consumer_explanation(topic, context)
        elif audience == "partner":
            return self._partner_explanation(topic, context)
        else:
            return self._internal_explanation(topic, context)
    
    def _consumer_explanation(self, topic: str, context: Dict) -> str:
        if "credit" in topic.lower():
            return (
                "Your credit score is calculated based on several factors including "
                "payment history (35%), amounts owed (30%), length of credit history (15%), "
                "new credit (10%), and credit mix (10%). To improve your score, focus on "
                "making on-time payments and keeping credit utilization below 30%."
            )
        return f"Here's what you need to know about {topic}..."
    
    def _partner_explanation(self, topic: str, context: Dict) -> str:
        factors = context.get("factors", [])
        factor_text = ", ".join([f"{f['name']} ({f['impact']})" for f in factors])
        return f"Decision based on key factors: {factor_text}. Risk model v2.3 applied."
    
    def _internal_explanation(self, topic: str, context: Dict) -> str:
        return f"Technical analysis: {context}"
    
    def _create_visualization(self, context: Dict) -> Dict[str, Any]:
        factors = context.get("factors", [])
        return {
            "type": "factor_breakdown",
            "data": [{"label": f["name"], "value": f["weight"], "sentiment": f["impact"]} for f in factors],
        }
    
    def _suggest_actions(self, context: Dict, audience: str) -> List[str]:
        if audience == "consumer":
            return [
                "Review your credit report for errors",
                "Set up autopay to avoid missed payments",
                "Consider a credit builder loan",
            ]
        return ["Review decision log", "Export analysis"]


class NotificationAgent(BaseAgent):
    """
    Agent 20: Notification Agent
    Orchestrate multi-channel notifications across email, SMS, push, and in-app.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="cross.notification.v1",
            name="Notification Agent",
            engine=Engine.CROSS_CUTTING,
            agent_type=AgentType.AMBASSADOR,
            risk_level=RiskLevel.LOW,
            faces=[Face.CONSUMER, Face.PARTNER, Face.INTERNAL],
            scope="Orchestrate multi-channel notifications",
            input_entities=["NotificationRequest", "UserPreferences", "TemplateLibrary"],
            output_entities=["NotificationEvent", "DeliveryStatus", "EngagementMetrics"],
            required_tools=["send_email", "send_sms", "send_push", "create_in_app"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        recipient_id = input_data.get("recipient_id")
        notification_type = input_data.get("type", "info")
        message = input_data.get("message", "")
        channels = input_data.get("channels", ["in_app"])
        priority = input_data.get("priority", "normal")
        
        # Get preferences
        preferences = await self._get_user_preferences(recipient_id)
        
        # Filter channels by preference
        allowed_channels = self._filter_channels(channels, preferences)
        
        # Render templates
        rendered = self._render_templates(message, notification_type, allowed_channels)
        
        # Send to each channel
        results = await self._send_notifications(recipient_id, rendered, priority)
        
        return {
            "status": "completed",
            "recipient_id": recipient_id,
            "channels_sent": list(results.keys()),
            "delivery_status": results,
        }
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        return {
            "email": True,
            "sms": True,
            "push": True,
            "in_app": True,
            "quiet_hours": {"start": "22:00", "end": "08:00"},
        }
    
    def _filter_channels(self, requested: List[str], prefs: Dict) -> List[str]:
        return [ch for ch in requested if prefs.get(ch, False)]
    
    def _render_templates(self, message: str, notif_type: str, channels: List[str]) -> Dict[str, str]:
        rendered = {}
        for channel in channels:
            if channel == "email":
                rendered[channel] = f"<html><body><h1>{notif_type.title()}</h1><p>{message}</p></body></html>"
            elif channel == "sms":
                rendered[channel] = f"CreditX: {message[:140]}"
            elif channel == "push":
                rendered[channel] = message[:100]
            else:
                rendered[channel] = message
        return rendered
    
    async def _send_notifications(self, recipient: str, rendered: Dict, priority: str) -> Dict[str, str]:
        results = {}
        for channel, content in rendered.items():
            results[channel] = "delivered"
            logger.info(f"Sent {channel} notification to {recipient}")
        return results


class OrchestrationAgent(BaseAgent):
    """
    Agent 21: Orchestration Agent (System)
    Coordinate workflows across all domain agents.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="cross.orchestration.v1",
            name="Orchestration Agent",
            engine=Engine.CROSS_CUTTING,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.MEDIUM,
            faces=[Face.INTERNAL],
            scope="Coordinate workflows across domain agents",
            input_entities=["WorkflowRequest", "AgentRegistry", "ExecutionContext"],
            output_entities=["WorkflowResult", "ExecutionTrace", "MetricsUpdate"],
            required_tools=["dispatch_agent", "aggregate_results", "handle_failure"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        workflow_type = input_data.get("workflow_type")
        steps = input_data.get("steps", [])
        
        results = []
        for step in steps:
            agent_id = step.get("agent_id")
            step_input = step.get("input", {})
            
            # Dispatch to agent
            result = await self._dispatch_agent(agent_id, step_input)
            results.append({"agent_id": agent_id, "result": result})
            
            # Check for failure
            if result.get("status") == "failed":
                await self._handle_failure(agent_id, result)
                break
        
        return {
            "status": "completed",
            "workflow_type": workflow_type,
            "steps_completed": len(results),
            "results": results,
        }
    
    async def _dispatch_agent(self, agent_id: str, input_data: Dict) -> Dict[str, Any]:
        return {"status": "completed", "agent_id": agent_id}
    
    async def _handle_failure(self, agent_id: str, result: Dict) -> None:
        logger.error(f"Agent {agent_id} failed: {result}")


class RecoveryAgent(BaseAgent):
    """
    Agent 22: Recovery Agent (System)
    Handle failures with automatic retry and escalation.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="cross.recovery.v1",
            name="Recovery Agent",
            engine=Engine.CROSS_CUTTING,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.LOW,
            faces=[Face.INTERNAL],
            scope="Handle failures with automatic retry and escalation",
            input_entities=["FailureEvent", "RetryPolicy", "EscalationRules"],
            output_entities=["RecoveryResult", "EscalationEvent", "MetricsUpdate"],
            required_tools=["retry_operation", "escalate", "notify_oncall"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        failure_event = input_data.get("failure_event", {})
        max_retries = input_data.get("max_retries", 3)
        
        # Classify error
        error_type = self._classify_error(failure_event)
        
        # Attempt recovery
        if error_type == "transient":
            recovery = await self._retry_with_backoff(failure_event, max_retries)
        else:
            recovery = {"success": False, "reason": "permanent_error"}
        
        # Escalate if needed
        if not recovery.get("success"):
            await self._escalate(failure_event, recovery)
        
        return {
            "status": "completed",
            "error_type": error_type,
            "recovery_success": recovery.get("success"),
            "retries_attempted": recovery.get("attempts", 0),
        }
    
    def _classify_error(self, event: Dict) -> str:
        transient = ["timeout", "connection_error", "rate_limit"]
        error = event.get("error_type", "")
        return "transient" if error in transient else "permanent"
    
    async def _retry_with_backoff(self, event: Dict, max_retries: int) -> Dict[str, Any]:
        import asyncio
        for attempt in range(max_retries):
            await asyncio.sleep(2 ** attempt)
            if attempt == max_retries - 1:
                return {"success": True, "attempts": attempt + 1}
        return {"success": False, "attempts": max_retries}
    
    async def _escalate(self, event: Dict, recovery: Dict) -> None:
        logger.warning(f"Escalating failure: {event}")
