"""
Outcome Engine Agents (4 agents)
Purpose: Turn financial goals into executable campaigns with measurable outcomes
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..core_agents import BaseAgent, AgentConfig, AgentType, Engine, RiskLevel, Face

logger = logging.getLogger(__name__)


class PlanGenerationAgent(BaseAgent):
    """
    Agent 1: Plan Generation Agent
    Creates personalized financial plans with measurable campaigns
    based on consumer goals, constraints, and current state.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="outcome.plan_generation.v1",
            name="Plan Generation Agent",
            engine=Engine.OUTCOME,
            agent_type=AgentType.AMBASSADOR,
            risk_level=RiskLevel.HIGH,
            faces=[Face.CONSUMER],
            scope="Create personalized financial plans with measurable campaigns",
            input_entities=["ConsumerGoals", "ConsumerConstraint", "ConsumerSnapshot", "ConsumerSecuritySummary"],
            output_entities=["SavingsPlan", "ActionItems", "CampaignPlaybook", "PredictionOutputs"],
            required_tools=["get_consumer_snapshot", "get_consumer_goals", "get_constraints", 
                           "generate_plan", "calculate_net_advantage", "estimate_probabilities"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan generation workflow."""
        consumer_id = input_data.get("consumer_id")
        goals = input_data.get("goals", [])
        
        # Phase 1: Analysis
        snapshot = await self._get_consumer_snapshot(consumer_id)
        constraints = await self._get_constraints(consumer_id)
        prioritized_goals = self._prioritize_goals(goals, snapshot)
        
        # Phase 2: Planning
        net_advantage = await self._calculate_net_advantage(prioritized_goals, snapshot)
        campaigns = self._generate_campaigns(prioritized_goals, constraints)
        action_items = self._define_action_items(campaigns)
        
        # Phase 3: Probability & Risk
        probabilities = await self._estimate_probabilities(action_items, snapshot)
        risk_adjusted = self._adjust_for_risk(net_advantage, probabilities)
        
        # Phase 4: Output
        plan = {
            "plan_id": f"plan_{consumer_id}_{self._generate_id()}",
            "consumer_id": consumer_id,
            "net_advantage": risk_adjusted,
            "confidence": probabilities.get("overall", 0.75),
            "active_campaigns": campaigns,
            "action_items": action_items,
            "milestones": self._create_milestones(campaigns),
        }
        
        return {"status": "completed", "plan": plan}
    
    async def _get_consumer_snapshot(self, consumer_id: str) -> Dict[str, Any]:
        if self.database:
            result = await self.database.fetch_one(
                "SELECT * FROM consumer_snapshots WHERE consumer_id = $1",
                consumer_id
            )
            return dict(result) if result else {}
        return {"consumer_id": consumer_id, "credit_score": 680, "income": 75000}
    
    async def _get_constraints(self, consumer_id: str) -> Dict[str, Any]:
        return {"max_monthly_payment": 500, "risk_tolerance": "moderate"}
    
    def _prioritize_goals(self, goals: List[Dict], snapshot: Dict) -> List[Dict]:
        return sorted(goals, key=lambda g: g.get("priority", 5))
    
    async def _calculate_net_advantage(self, goals: List[Dict], snapshot: Dict) -> float:
        base_score = snapshot.get("credit_score", 650)
        improvement = sum(g.get("expected_lift", 10) for g in goals)
        return improvement * 100
    
    def _generate_campaigns(self, goals: List[Dict], constraints: Dict) -> List[Dict]:
        campaigns = []
        for goal in goals[:3]:
            campaigns.append({
                "campaign_type": goal.get("type", "Score Lift Track"),
                "target": goal.get("target", "40_point_increase"),
                "horizon": goal.get("horizon", "90_days"),
                "key_actions": ["review_report", "dispute_errors", "optimize_utilization"],
            })
        return campaigns
    
    def _define_action_items(self, campaigns: List[Dict]) -> List[Dict]:
        items = []
        for campaign in campaigns:
            for action in campaign.get("key_actions", []):
                items.append({
                    "action": action,
                    "effort": "low",
                    "impact": "high",
                    "automated": action in ["review_report"],
                })
        return items
    
    async def _estimate_probabilities(self, items: List[Dict], snapshot: Dict) -> Dict[str, float]:
        return {"overall": 0.78, "per_action": {item["action"]: 0.85 for item in items}}
    
    def _adjust_for_risk(self, net_advantage: float, probabilities: Dict) -> float:
        return net_advantage * probabilities.get("overall", 0.75)
    
    def _create_milestones(self, campaigns: List[Dict]) -> List[Dict]:
        return [
            {"milestone": "25%", "target_date": "30_days"},
            {"milestone": "50%", "target_date": "60_days"},
            {"milestone": "75%", "target_date": "80_days"},
            {"milestone": "100%", "target_date": "90_days"},
        ]
    
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]


class OutcomeEvaluationAgent(BaseAgent):
    """
    Agent 2: Outcome Evaluation Agent
    Track actual vs. projected outcomes for plans and campaigns.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="outcome.evaluation.v1",
            name="Outcome Evaluation Agent",
            engine=Engine.OUTCOME,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.LOW,
            faces=[Face.INTERNAL],
            scope="Track actual vs. projected outcomes for plans and campaigns",
            input_entities=["SavingsPlan", "OutcomeTracks", "ConsumerSnapshot", "CampaignPlaybook"],
            output_entities=["OutcomeTracks", "PredictionOutputs", "MilestoneEvents"],
            required_tools=["get_outcome_tracks", "update_outcome_tracks", "detect_milestones"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        plan_id = input_data.get("plan_id")
        consumer_id = input_data.get("consumer_id")
        
        # Fetch current state
        tracks = await self._get_outcome_tracks(plan_id)
        current_snapshot = await self._get_current_snapshot(consumer_id)
        
        # Compare projected vs actual
        progress = self._calculate_progress(tracks, current_snapshot)
        milestones = self._detect_milestones(progress)
        
        # Update tracks
        updated_tracks = await self._update_tracks(plan_id, progress, milestones)
        
        return {
            "status": "completed",
            "track_id": updated_tracks.get("id"),
            "progress_pct": progress.get("percentage", 0),
            "milestones_achieved": milestones,
            "velocity": progress.get("velocity", 0),
        }
    
    async def _get_outcome_tracks(self, plan_id: str) -> Dict[str, Any]:
        return {"plan_id": plan_id, "baseline": 680, "target": 720, "current": 695}
    
    async def _get_current_snapshot(self, consumer_id: str) -> Dict[str, Any]:
        return {"credit_score": 698, "last_updated": "2026-01-16"}
    
    def _calculate_progress(self, tracks: Dict, snapshot: Dict) -> Dict[str, Any]:
        baseline = tracks.get("baseline", 680)
        target = tracks.get("target", 720)
        current = snapshot.get("credit_score", baseline)
        total_needed = target - baseline
        achieved = current - baseline
        percentage = (achieved / total_needed * 100) if total_needed > 0 else 0
        return {"percentage": round(percentage, 1), "velocity": achieved / 4, "current": current}
    
    def _detect_milestones(self, progress: Dict) -> List[int]:
        pct = progress.get("percentage", 0)
        achieved = []
        for milestone in [25, 50, 75, 100]:
            if pct >= milestone:
                achieved.append(milestone)
        return achieved
    
    async def _update_tracks(self, plan_id: str, progress: Dict, milestones: List) -> Dict[str, Any]:
        return {"id": f"track_{plan_id}", "progress": progress, "milestones": milestones}


class CampaignTuningAgent(BaseAgent):
    """
    Agent 3: Campaign Tuning Agent
    Analyze campaign performance and recommend config changes.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="outcome.campaign_tuning.v1",
            name="Campaign Tuning Agent",
            engine=Engine.OUTCOME,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.MEDIUM,
            faces=[Face.INTERNAL],
            scope="Analyze campaign performance and recommend config changes",
            input_entities=["CampaignOutcomeSummary", "CampaignPlaybook", "PredictionOutputs"],
            output_entities=["CampaignConfigRecommendations", "RecalibrationReport"],
            required_tools=["get_campaign_summary", "simulate_config_change", "propose_experiment"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        campaign_type = input_data.get("campaign_type", "Score Lift Track")
        
        # Aggregate performance
        summary = await self._get_campaign_summary(campaign_type)
        
        # Identify underperformers
        underperformers = self._identify_underperformers(summary)
        
        # Simulate changes
        simulations = await self._simulate_changes(underperformers)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(simulations)
        
        return {
            "status": "completed",
            "campaign_type": campaign_type,
            "current_completion_rate": summary.get("completion_rate", 0.63),
            "recommendations": recommendations,
            "approval_required": True,
        }
    
    async def _get_campaign_summary(self, campaign_type: str) -> Dict[str, Any]:
        return {"campaign_type": campaign_type, "completion_rate": 0.63, "cohort_size": 2847}
    
    def _identify_underperformers(self, summary: Dict) -> List[Dict]:
        return [{"action": "update_profile", "completion_rate": 0.45}]
    
    async def _simulate_changes(self, underperformers: List) -> List[Dict]:
        return [{"change": "reorder_actions", "projected_improvement": 0.08}]
    
    def _generate_recommendations(self, simulations: List) -> List[Dict]:
        return [{
            "recommendation_id": "rec_001",
            "proposed_change": "Reorder actions: [validate_bureau, dispute_errors, update_profile]",
            "expected_roi": 8.3,
        }]


class ReferralImpactAgent(BaseAgent):
    """
    Agent 4: Referral Impact Agent
    Identify partnership opportunities and track referral effectiveness.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="outcome.referral_impact.v1",
            name="Referral Impact Agent",
            engine=Engine.OUTCOME,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.LOW,
            faces=[Face.INTERNAL, Face.PARTNER],
            scope="Identify partnership opportunities, track referral effectiveness",
            input_entities=["ConsumerOutcomeSummary", "PartnerOutcomeSummary", "MarketPartnerDirectory"],
            output_entities=["ReferralRecommendations", "ReferralImpactSummary", "ConversionTracks"],
            required_tools=["get_outcome_summary", "get_partner_directory", "calculate_referral_fit"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        consumer_id = input_data.get("consumer_id")
        
        # Detect opportunities
        opportunities = await self._detect_opportunities(consumer_id)
        
        # Match to partners
        matches = await self._match_partners(opportunities)
        
        # Calculate impact
        impact = self._calculate_impact(matches)
        
        return {
            "status": "completed",
            "consumer_id": consumer_id,
            "referral_recommendations": matches,
            "estimated_lift": impact.get("net_advantage_lift", 2100),
        }
    
    async def _detect_opportunities(self, consumer_id: str) -> List[Dict]:
        return [{"type": "debt_consolidation", "gap_to_goal": 10}]
    
    async def _match_partners(self, opportunities: List) -> List[Dict]:
        return [{
            "partner_id": "LoanPartner123",
            "recommendation_reason": "Debt consolidation opportunity",
            "conversion_probability": 0.65,
        }]
    
    def _calculate_impact(self, matches: List) -> Dict[str, float]:
        return {"net_advantage_lift": 2100}
