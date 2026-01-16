export type Face = 'consumer' | 'partner' | 'internal';

export type AgentEngine = 'outcome' | 'rights_trust' | 'risk_security' | 'market_capital';

export type HitlStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface TenantContext {
  tenantId: string;
  face: Face;
  userId?: string;
  consumerId?: string;
  partnerId?: string;
}

export interface Agent {
  id: string;
  name: string;
  engine: AgentEngine;
  description: string;
  status: 'active' | 'inactive' | 'deprecated';
  capabilities: string[];
}

export interface AgentExecution {
  executionId: string;
  agentId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  result?: Record<string, unknown>;
  error?: string;
}

export interface HitlRequest {
  id: string;
  executionId: string;
  agentId: string;
  action: string;
  reason: string;
  riskLevel: RiskLevel;
  status: HitlStatus;
  payload: Record<string, unknown>;
  createdAt: string;
  expiresAt: string;
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface CreditScore {
  score: number;
  provider: string;
  factors: ScoreFactor[];
  lastUpdated: string;
}

export interface ScoreFactor {
  factor: string;
  impact: 'positive' | 'negative' | 'neutral';
  weight: number;
  score: number;
}

export interface Dispute {
  id: string;
  consumerId: string;
  item: string;
  reason: string;
  status: 'open' | 'investigating' | 'resolved' | 'rejected';
  createdAt: string;
  resolvedAt?: string;
  outcome?: string;
}

export interface Loan {
  id: string;
  borrowerId: string;
  partnerId: string;
  amount: number;
  apr: number;
  term: number;
  status: 'active' | 'delinquent' | 'paid_off' | 'default';
  originationDate: string;
  riskTier: RiskLevel;
}

export interface UnderwritingApplication {
  id: string;
  applicantId: string;
  partnerId: string;
  requestedAmount: number;
  creditScore: number;
  dti: number;
  status: 'pending' | 'approved' | 'declined' | 'manual_review';
  submittedAt: string;
  decisionAt?: string;
}

export interface ComplianceCheck {
  id: string;
  name: string;
  category: string;
  status: 'passed' | 'failed' | 'warning';
  lastChecked: string;
  details?: string;
}

export interface FairnessMetric {
  metric: string;
  value: number;
  threshold: number;
  status: 'compliant' | 'non_compliant' | 'warning';
  demographic?: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  resourceId: string;
  details: Record<string, unknown>;
  tenantId: string;
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency: number;
  uptime: number;
  lastChecked: string;
}

export interface ApiResponse<T> {
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
  };
  error?: {
    code: string;
    message: string;
  };
}
