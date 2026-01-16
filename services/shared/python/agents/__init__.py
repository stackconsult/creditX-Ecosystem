"""
CreditX Agent Implementations
22 domain agents across 4 engines + 2 cross-cutting agents
"""
from .outcome_agents import (
    PlanGenerationAgent,
    OutcomeEvaluationAgent,
    CampaignTuningAgent,
    ReferralImpactAgent,
)
from .rights_trust_agents import (
    ConsentScopeAgent,
    RightsRequestAgent,
    DisputeAdvocacyAgent,
    FairnessMonitorAgent,
    AuditComplianceAgent,
)
from .risk_security_agents import (
    ThreatIntelAgent,
    AlertAggregatorAgent,
    IncidentResponseAgent,
    RemediationAgent,
)
from .market_capital_agents import (
    UnderwritingDecisionAgent,
    PortfolioAnalysisAgent,
    PricingOptimizationAgent,
    LoanPackagingAgent,
    CapitalAllocationAgent,
)
from .cross_cutting_agents import (
    ExplainerAgent,
    NotificationAgent,
)

__all__ = [
    "PlanGenerationAgent",
    "OutcomeEvaluationAgent",
    "CampaignTuningAgent",
    "ReferralImpactAgent",
    "ConsentScopeAgent",
    "RightsRequestAgent",
    "DisputeAdvocacyAgent",
    "FairnessMonitorAgent",
    "AuditComplianceAgent",
    "ThreatIntelAgent",
    "AlertAggregatorAgent",
    "IncidentResponseAgent",
    "RemediationAgent",
    "UnderwritingDecisionAgent",
    "PortfolioAnalysisAgent",
    "PricingOptimizationAgent",
    "LoanPackagingAgent",
    "CapitalAllocationAgent",
    "ExplainerAgent",
    "NotificationAgent",
]
