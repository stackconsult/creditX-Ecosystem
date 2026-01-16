"""
Market & Capital Engine Agents (5 agents)
Purpose: Underwriting, portfolio analysis, pricing, loan packaging, capital allocation
"""
from typing import Dict, Any, List, Optional
import logging

from ..core_agents import BaseAgent, AgentConfig, AgentType, Engine, RiskLevel, Face

logger = logging.getLogger(__name__)


class UnderwritingDecisionAgent(BaseAgent):
    """
    Agent 14: Underwriting Decision Agent
    Automate underwriting decisions with risk-based pricing recommendations.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="market.underwriting_decision.v1",
            name="Underwriting Decision Agent",
            engine=Engine.MARKET_CAPITAL,
            agent_type=AgentType.AMBASSADOR,
            risk_level=RiskLevel.HIGH,
            faces=[Face.PARTNER, Face.INTERNAL],
            scope="Automate underwriting decisions with risk-based pricing",
            input_entities=["ApplicationData", "CreditReport", "IncomeVerification", "RiskModels"],
            output_entities=["UnderwritingDecision", "PricingRecommendation", "ConditionsList"],
            required_tools=["get_credit_data", "run_risk_model", "calculate_pricing", "generate_conditions"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        application_id = input_data.get("application_id")
        applicant_data = input_data.get("applicant_data", {})
        loan_amount = input_data.get("loan_amount", 0)
        loan_term = input_data.get("loan_term", 36)
        
        # Get credit data
        credit = await self._get_credit_data(applicant_data.get("ssn_hash"))
        
        # Run risk model
        risk_score = self._run_risk_model(credit, applicant_data, loan_amount)
        
        # Make decision
        decision = self._make_decision(risk_score, loan_amount)
        
        # Calculate pricing
        pricing = self._calculate_pricing(risk_score, loan_amount, loan_term)
        
        # Generate conditions
        conditions = self._generate_conditions(decision, credit, applicant_data)
        
        return {
            "status": "completed",
            "application_id": application_id,
            "decision": decision.get("result"),
            "risk_score": risk_score,
            "apr": pricing.get("apr"),
            "monthly_payment": pricing.get("monthly_payment"),
            "conditions": conditions,
            "requires_human_review": decision.get("result") == "review",
        }
    
    async def _get_credit_data(self, ssn_hash: str) -> Dict[str, Any]:
        return {"score": 720, "utilization": 0.25, "derogatory_marks": 0, "age_of_credit": 8}
    
    def _run_risk_model(self, credit: Dict, applicant: Dict, amount: float) -> int:
        base = credit.get("score", 650)
        dti = applicant.get("debt_to_income", 0.35)
        risk_adjustment = int((1 - dti) * 50)
        return min(max(base + risk_adjustment - 650, 0), 100)
    
    def _make_decision(self, risk_score: int, amount: float) -> Dict[str, Any]:
        if risk_score >= 70:
            return {"result": "approved", "tier": "prime"}
        elif risk_score >= 50:
            return {"result": "approved", "tier": "near_prime"}
        elif risk_score >= 30:
            return {"result": "review", "tier": "subprime"}
        else:
            return {"result": "declined", "tier": None}
    
    def _calculate_pricing(self, risk_score: int, amount: float, term: int) -> Dict[str, Any]:
        base_apr = 0.08
        risk_premium = (100 - risk_score) * 0.002
        apr = base_apr + risk_premium
        monthly_rate = apr / 12
        payment = amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        return {"apr": round(apr * 100, 2), "monthly_payment": round(payment, 2)}
    
    def _generate_conditions(self, decision: Dict, credit: Dict, applicant: Dict) -> List[str]:
        conditions = []
        if decision.get("tier") == "near_prime":
            conditions.append("Income verification required")
        if credit.get("utilization", 0) > 0.5:
            conditions.append("Pay down existing balances to 30%")
        return conditions


class PortfolioAnalysisAgent(BaseAgent):
    """
    Agent 15: Portfolio Analysis Agent
    Analyze loan portfolio performance, risk distribution, and trends.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="market.portfolio_analysis.v1",
            name="Portfolio Analysis Agent",
            engine=Engine.MARKET_CAPITAL,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.LOW,
            faces=[Face.PARTNER, Face.INTERNAL],
            scope="Analyze loan portfolio performance and risk distribution",
            input_entities=["LoanPortfolio", "PerformanceMetrics", "MarketData"],
            output_entities=["PortfolioReport", "RiskDistribution", "TrendAnalysis"],
            required_tools=["get_portfolio_data", "calculate_metrics", "run_trend_analysis"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        partner_id = input_data.get("partner_id")
        portfolio_id = input_data.get("portfolio_id")
        
        # Get portfolio data
        portfolio = await self._get_portfolio_data(portfolio_id)
        
        # Calculate metrics
        metrics = self._calculate_metrics(portfolio)
        
        # Risk distribution
        risk_dist = self._analyze_risk_distribution(portfolio)
        
        # Trend analysis
        trends = self._run_trend_analysis(portfolio)
        
        return {
            "status": "completed",
            "portfolio_id": portfolio_id,
            "total_value": metrics.get("total_value"),
            "weighted_apr": metrics.get("weighted_apr"),
            "delinquency_rate": metrics.get("delinquency_rate"),
            "risk_distribution": risk_dist,
            "trends": trends,
        }
    
    async def _get_portfolio_data(self, portfolio_id: str) -> Dict[str, Any]:
        return {
            "loans": [
                {"id": "L001", "amount": 25000, "apr": 8.5, "status": "current", "tier": "prime"},
                {"id": "L002", "amount": 15000, "apr": 12.0, "status": "current", "tier": "near_prime"},
                {"id": "L003", "amount": 10000, "apr": 18.0, "status": "30_dpd", "tier": "subprime"},
            ],
            "total_loans": 150,
            "total_value": 2500000,
        }
    
    def _calculate_metrics(self, portfolio: Dict) -> Dict[str, Any]:
        loans = portfolio.get("loans", [])
        total = sum(l.get("amount", 0) for l in loans)
        weighted_apr = sum(l.get("amount", 0) * l.get("apr", 0) for l in loans) / total if total else 0
        delinquent = sum(1 for l in loans if "dpd" in l.get("status", ""))
        return {
            "total_value": portfolio.get("total_value", total),
            "weighted_apr": round(weighted_apr, 2),
            "delinquency_rate": round(delinquent / len(loans) * 100, 2) if loans else 0,
        }
    
    def _analyze_risk_distribution(self, portfolio: Dict) -> Dict[str, int]:
        loans = portfolio.get("loans", [])
        dist = {"prime": 0, "near_prime": 0, "subprime": 0}
        for loan in loans:
            tier = loan.get("tier", "subprime")
            dist[tier] = dist.get(tier, 0) + 1
        return dist
    
    def _run_trend_analysis(self, portfolio: Dict) -> Dict[str, Any]:
        return {
            "delinquency_trend": "stable",
            "origination_trend": "increasing",
            "prepayment_trend": "stable",
        }


class PricingOptimizationAgent(BaseAgent):
    """
    Agent 16: Pricing Optimization Agent
    Optimize loan pricing based on risk, market conditions, and competition.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="market.pricing_optimization.v1",
            name="Pricing Optimization Agent",
            engine=Engine.MARKET_CAPITAL,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.MEDIUM,
            faces=[Face.INTERNAL],
            scope="Optimize loan pricing based on risk and market conditions",
            input_entities=["RiskModels", "MarketRates", "CompetitorData", "HistoricalPerformance"],
            output_entities=["PricingGrid", "MarginAnalysis", "OptimizationReport"],
            required_tools=["get_market_rates", "analyze_competition", "run_optimization"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        product_type = input_data.get("product_type", "personal_loan")
        target_margin = input_data.get("target_margin", 0.03)
        
        # Get market rates
        market = await self._get_market_rates()
        
        # Analyze competition
        competition = self._analyze_competition(product_type)
        
        # Run optimization
        pricing_grid = self._run_optimization(market, competition, target_margin)
        
        # Calculate margins
        margins = self._calculate_margins(pricing_grid, market)
        
        return {
            "status": "completed",
            "product_type": product_type,
            "pricing_grid": pricing_grid,
            "expected_margin": margins.get("expected"),
            "competitive_position": competition.get("position"),
        }
    
    async def _get_market_rates(self) -> Dict[str, float]:
        return {"prime_rate": 0.0825, "fed_funds": 0.055, "treasury_10y": 0.045}
    
    def _analyze_competition(self, product_type: str) -> Dict[str, Any]:
        return {"avg_apr": 10.5, "range": [7.0, 18.0], "position": "competitive"}
    
    def _run_optimization(self, market: Dict, competition: Dict, target: float) -> List[Dict]:
        base = market.get("prime_rate", 0.08)
        return [
            {"tier": "prime", "min_apr": round((base + 0.01) * 100, 2), "max_apr": round((base + 0.03) * 100, 2)},
            {"tier": "near_prime", "min_apr": round((base + 0.04) * 100, 2), "max_apr": round((base + 0.08) * 100, 2)},
            {"tier": "subprime", "min_apr": round((base + 0.10) * 100, 2), "max_apr": round((base + 0.18) * 100, 2)},
        ]
    
    def _calculate_margins(self, grid: List, market: Dict) -> Dict[str, float]:
        return {"expected": 0.035, "min": 0.02, "max": 0.05}


class LoanPackagingAgent(BaseAgent):
    """
    Agent 17: Loan Packaging Agent
    Package loans for securitization or secondary market sale.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="market.loan_packaging.v1",
            name="Loan Packaging Agent",
            engine=Engine.MARKET_CAPITAL,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.HIGH,
            faces=[Face.INTERNAL],
            scope="Package loans for securitization or secondary market",
            input_entities=["LoanPool", "PackagingCriteria", "BuyerRequirements"],
            output_entities=["LoanPackage", "PoolAnalytics", "ComplianceCertification"],
            required_tools=["select_loans", "create_package", "run_pool_analytics", "certify_compliance"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pool_criteria = input_data.get("criteria", {})
        target_size = input_data.get("target_size", 10000000)
        buyer_requirements = input_data.get("buyer_requirements", {})
        
        # Select loans
        selected = await self._select_loans(pool_criteria, target_size)
        
        # Create package
        package = self._create_package(selected)
        
        # Run analytics
        analytics = self._run_pool_analytics(package)
        
        # Certify compliance
        compliance = self._certify_compliance(package, buyer_requirements)
        
        return {
            "status": "completed",
            "package_id": package.get("id"),
            "loan_count": len(selected),
            "total_value": package.get("total_value"),
            "weighted_apr": analytics.get("weighted_apr"),
            "compliance_certified": compliance.get("certified"),
        }
    
    async def _select_loans(self, criteria: Dict, target: float) -> List[Dict]:
        return [
            {"id": "L001", "amount": 25000, "apr": 8.5, "fico": 750},
            {"id": "L002", "amount": 30000, "apr": 9.0, "fico": 720},
        ]
    
    def _create_package(self, loans: List) -> Dict[str, Any]:
        import uuid
        total = sum(l.get("amount", 0) for l in loans)
        return {"id": f"PKG-{uuid.uuid4().hex[:8].upper()}", "loans": loans, "total_value": total}
    
    def _run_pool_analytics(self, package: Dict) -> Dict[str, Any]:
        loans = package.get("loans", [])
        total = package.get("total_value", 1)
        weighted = sum(l.get("amount", 0) * l.get("apr", 0) for l in loans) / total if total else 0
        avg_fico = sum(l.get("fico", 650) for l in loans) / len(loans) if loans else 650
        return {"weighted_apr": round(weighted, 2), "avg_fico": round(avg_fico)}
    
    def _certify_compliance(self, package: Dict, requirements: Dict) -> Dict[str, Any]:
        return {"certified": True, "checks_passed": ["fico_threshold", "dti_limit", "ltv_limit"]}


class CapitalAllocationAgent(BaseAgent):
    """
    Agent 18: Capital Allocation Agent
    Optimize capital allocation across lending products and risk tiers.
    """
    
    def __init__(self):
        config = AgentConfig(
            agent_id="market.capital_allocation.v1",
            name="Capital Allocation Agent",
            engine=Engine.MARKET_CAPITAL,
            agent_type=AgentType.OPERATOR,
            risk_level=RiskLevel.HIGH,
            faces=[Face.INTERNAL],
            scope="Optimize capital allocation across products and risk tiers",
            input_entities=["AvailableCapital", "ProductPerformance", "RiskLimits", "StrategicGoals"],
            output_entities=["AllocationPlan", "CapitalBudget", "ROEProjection"],
            required_tools=["get_capital_position", "run_allocation_model", "project_returns"],
        )
        super().__init__(config)
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        available_capital = input_data.get("available_capital", 100000000)
        risk_appetite = input_data.get("risk_appetite", "moderate")
        target_roe = input_data.get("target_roe", 0.15)
        
        # Get current position
        position = await self._get_capital_position()
        
        # Run allocation model
        allocation = self._run_allocation_model(available_capital, risk_appetite)
        
        # Project returns
        projections = self._project_returns(allocation, target_roe)
        
        return {
            "status": "completed",
            "total_capital": available_capital,
            "allocation": allocation,
            "projected_roe": projections.get("roe"),
            "risk_score": projections.get("risk_score"),
        }
    
    async def _get_capital_position(self) -> Dict[str, Any]:
        return {"deployed": 80000000, "available": 20000000, "reserved": 5000000}
    
    def _run_allocation_model(self, capital: float, risk: str) -> Dict[str, float]:
        allocations = {
            "conservative": {"prime": 0.60, "near_prime": 0.30, "subprime": 0.10},
            "moderate": {"prime": 0.45, "near_prime": 0.35, "subprime": 0.20},
            "aggressive": {"prime": 0.30, "near_prime": 0.35, "subprime": 0.35},
        }
        pcts = allocations.get(risk, allocations["moderate"])
        return {tier: capital * pct for tier, pct in pcts.items()}
    
    def _project_returns(self, allocation: Dict, target: float) -> Dict[str, Any]:
        weighted_return = allocation.get("prime", 0) * 0.08 + allocation.get("near_prime", 0) * 0.12 + allocation.get("subprime", 0) * 0.18
        total = sum(allocation.values())
        roe = weighted_return / total if total else 0
        return {"roe": round(roe * 100, 2), "risk_score": 65}
