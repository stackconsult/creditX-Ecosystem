/**
 * CreditX Type Definitions
 */

// ============================================================================
// COMMON TYPES
// ============================================================================

export type Status = 'active' | 'pending' | 'completed' | 'failed' | 'cancelled';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type Face = 'consumer' | 'partner' | 'internal';

export interface Alert {
  id: number | string;
  type: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  date?: string;
}

// ============================================================================
// CONSUMER TYPES
// ============================================================================

export interface CreditReport {
  score: number;
  scoreChange: number;
  scoreTrend: number[];
  scoreFactors: ScoreFactor[];
  accounts: CreditAccount[];
  inquiries: CreditInquiry[];
}

export interface ScoreFactor {
  factor: string;
  impact: 'positive' | 'neutral' | 'negative';
  score: number;
  weight: number;
}

export interface CreditAccount {
  name: string;
  type: string;
  balance: number;
  limit?: number;
  original?: number;
  status: string;
}

export interface CreditInquiry {
  lender: string;
  date: string;
  type: string;
}

export interface Dispute {
  id: string;
  bureau: string;
  item: string;
  status: 'draft' | 'in_progress' | 'resolved' | 'rejected';
  filed: string;
  dueDate?: string;
  resolvedDate?: string;
  outcome?: string;
}

export interface SavingsPlan {
  id: string;
  name: string;
  target: number;
  progress: number;
  startScore: number;
  currentScore: number;
  dueDate: string;
  campaigns: number;
}

export interface RightsRequest {
  id: string;
  type: 'export' | 'delete' | 'restrict';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  requestedAt: string;
  completedAt?: string;
}

// ============================================================================
// PARTNER TYPES
// ============================================================================

export interface Portfolio {
  totalAssets: number;
  activeLoans: number;
  avgCreditScore: number;
  defaultRate: number;
  delinquencyRate: number;
  avgLoanSize: number;
  totalBorrowers: number;
  yieldRate: number;
}

export interface Loan {
  id: string;
  borrower: string;
  amount: number;
  apr: number;
  term: number;
  status: 'current' | '30_dpd' | '60_dpd' | '90_dpd' | 'default' | 'paid_off';
  score: number;
  originated: string;
}

export interface UnderwritingApplication {
  id: string;
  applicant: string;
  amount: number;
  status: 'pending_review' | 'pending_docs' | 'approved' | 'declined' | 'withdrawn';
  score: number;
  submitted: string;
  riskTier: 'prime' | 'near_prime' | 'subprime';
  apr?: number;
  reason?: string;
}

export interface RiskDistribution {
  tier: string;
  count: number;
  percentage: number;
  avgApr: number;
}

// ============================================================================
// INTERNAL TYPES
// ============================================================================

export interface SystemStats {
  activeAgents: number;
  totalAgents: number;
  pendingHitl: number;
  threatsToday: number;
  complianceScore: number;
  uptime: number;
  requestsToday: number;
  avgLatency: number;
}

export interface Service {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  latency: number;
  cpu: number;
  memory: number;
  requests: number;
}

export interface Agent {
  id: string;
  name: string;
  engine: string;
  type: 'assistant' | 'operator' | 'ambassador';
  status: 'active' | 'inactive' | 'error';
  executions: number;
  avgTime: number;
}

export interface HitlRequest {
  id: string;
  agent: string;
  task: string;
  risk: Severity;
  consumer: string;
  amount: number | null;
  waitTime: number;
}

export interface AuditLog {
  id: string;
  action: string;
  agent: string | null;
  user: string;
  timestamp: string;
  status: string;
}

export interface Tenant {
  id: string;
  name: string;
  domain: string;
  modules: string[];
  users: number;
  status: 'active' | 'trial' | 'suspended';
}

export interface Threat {
  id: string;
  type: string;
  severity: Severity;
  source: string;
  status: 'investigating' | 'blocked' | 'resolved';
  detected: string;
}

// ============================================================================
// COMPONENT PROPS
// ============================================================================

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  color?: 'default' | 'success' | 'warning' | 'error' | 'info';
}

export interface DataTableColumn<T> {
  key: keyof T | string;
  header: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

export interface StatusBadgeProps {
  status: string;
  variant?: 'default' | 'outline';
  size?: 'sm' | 'md';
}
