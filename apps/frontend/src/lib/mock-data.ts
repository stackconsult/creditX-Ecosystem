/**
 * CreditX Mock Data Service
 * Realistic mock data for all OS faces
 */

// ============================================================================
// CONSUMER DATA
// ============================================================================

export const mockConsumerData = {
  profile: {
    id: 'consumer_001',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@email.com',
    memberSince: '2023-06-15',
  },
  
  creditReport: {
    score: 720,
    scoreChange: +12,
    scoreTrend: [685, 692, 698, 705, 712, 720],
    scoreFactors: [
      { factor: 'Payment History', impact: 'positive', score: 95, weight: 35 },
      { factor: 'Credit Utilization', impact: 'positive', score: 22, weight: 30 },
      { factor: 'Credit Age', impact: 'neutral', score: 8, weight: 15 },
      { factor: 'Credit Mix', impact: 'positive', score: 4, weight: 10 },
      { factor: 'New Credit', impact: 'neutral', score: 2, weight: 10 },
    ],
    accounts: [
      { name: 'Chase Sapphire', type: 'Credit Card', balance: 2450, limit: 15000, status: 'current' },
      { name: 'Citi Double Cash', type: 'Credit Card', balance: 890, limit: 8000, status: 'current' },
      { name: 'Auto Loan', type: 'Installment', balance: 12400, original: 25000, status: 'current' },
      { name: 'Student Loan', type: 'Installment', balance: 18200, original: 35000, status: 'current' },
    ],
    inquiries: [
      { lender: 'Capital One', date: '2025-11-15', type: 'Credit Card' },
      { lender: 'Toyota Financial', date: '2025-08-22', type: 'Auto Loan' },
    ],
  },

  disputes: [
    { id: 'DSP-001', bureau: 'Experian', item: 'Late Payment - Chase', status: 'in_progress', filed: '2026-01-10', dueDate: '2026-02-10' },
    { id: 'DSP-002', bureau: 'TransUnion', item: 'Incorrect Balance', status: 'resolved', filed: '2025-12-01', resolvedDate: '2025-12-28', outcome: 'removed' },
  ],

  plans: [
    { id: 'PLN-001', name: 'Score Lift 40', target: 760, progress: 45, startScore: 680, currentScore: 720, dueDate: '2026-04-01', campaigns: 3 },
  ],

  alerts: [
    { id: 1, type: 'success', title: 'Dispute Resolved', message: 'Your dispute with TransUnion was resolved in your favor', date: '2025-12-28' },
    { id: 2, type: 'info', title: 'Credit Report Updated', message: 'Your Experian report was refreshed', date: '2026-01-15' },
    { id: 3, type: 'warning', title: 'Payment Due', message: 'Chase Sapphire payment due in 5 days', date: '2026-01-16' },
  ],

  rightsRequests: [
    { id: 'RR-001', type: 'export', status: 'completed', requestedAt: '2025-11-01', completedAt: '2025-11-03' },
  ],
};

// ============================================================================
// PARTNER DATA
// ============================================================================

export const mockPartnerData = {
  profile: {
    id: 'partner_001',
    name: 'Apex Lending',
    type: 'Consumer Lender',
    since: '2024-01-15',
  },

  portfolio: {
    totalAssets: 125000000,
    activeLoans: 1245,
    avgCreditScore: 680,
    defaultRate: 2.3,
    delinquencyRate: 4.8,
    avgLoanSize: 45000,
    totalBorrowers: 1180,
    yieldRate: 8.5,
  },

  portfolioTrend: [
    { month: 'Aug', value: 98000000, loans: 980 },
    { month: 'Sep', value: 105000000, loans: 1050 },
    { month: 'Oct', value: 112000000, loans: 1120 },
    { month: 'Nov', value: 118000000, loans: 1180 },
    { month: 'Dec', value: 122000000, loans: 1220 },
    { month: 'Jan', value: 125000000, loans: 1245 },
  ],

  loans: [
    { id: 'LN-2024-001', borrower: 'John Smith', amount: 50000, apr: 8.5, term: 60, status: 'current', score: 720, originated: '2024-06-15' },
    { id: 'LN-2024-002', borrower: 'Maria Garcia', amount: 35000, apr: 10.2, term: 48, status: 'current', score: 685, originated: '2024-07-22' },
    { id: 'LN-2024-003', borrower: 'David Lee', amount: 75000, apr: 7.9, term: 72, status: '30_dpd', score: 650, originated: '2024-05-10' },
    { id: 'LN-2024-004', borrower: 'Emily Chen', amount: 25000, apr: 12.5, term: 36, status: 'current', score: 620, originated: '2024-08-30' },
    { id: 'LN-2024-005', borrower: 'Robert Wilson', amount: 100000, apr: 6.9, term: 84, status: 'current', score: 780, originated: '2024-04-05' },
  ],

  underwriting: [
    { id: 'UW-2026-001', applicant: 'Alice Brown', amount: 50000, status: 'pending_review', score: 695, submitted: '2026-01-16', riskTier: 'near_prime' },
    { id: 'UW-2026-002', applicant: 'Michael Davis', amount: 75000, status: 'approved', score: 740, submitted: '2026-01-15', riskTier: 'prime', apr: 7.5 },
    { id: 'UW-2026-003', applicant: 'Jennifer Martinez', amount: 120000, status: 'pending_docs', score: 710, submitted: '2026-01-14', riskTier: 'prime' },
    { id: 'UW-2026-004', applicant: 'William Taylor', amount: 30000, status: 'declined', score: 580, submitted: '2026-01-13', riskTier: 'subprime', reason: 'DTI too high' },
  ],

  riskDistribution: [
    { tier: 'Prime', count: 520, percentage: 42, avgApr: 7.2 },
    { tier: 'Near Prime', count: 480, percentage: 38, avgApr: 10.5 },
    { tier: 'Subprime', count: 245, percentage: 20, avgApr: 16.8 },
  ],

  complianceScore: 96,
  fairnessScore: 92,
  
  alerts: [
    { id: 1, type: 'warning', message: '3 loans approaching 60-day delinquency threshold' },
    { id: 2, type: 'info', message: 'Quarterly compliance review due in 5 days' },
  ],
};

// ============================================================================
// INTERNAL DATA
// ============================================================================

export const mockInternalData = {
  systemStats: {
    activeAgents: 18,
    totalAgents: 22,
    pendingHitl: 5,
    threatsToday: 3,
    complianceScore: 94,
    uptime: 99.97,
    requestsToday: 45230,
    avgLatency: 42,
  },

  services: [
    { name: 'creditx-service', status: 'healthy', latency: 45, cpu: 32, memory: 58, requests: 12500 },
    { name: 'threat-service', status: 'healthy', latency: 32, cpu: 28, memory: 45, requests: 8900 },
    { name: 'guardian-service', status: 'healthy', latency: 28, cpu: 22, memory: 42, requests: 6700 },
    { name: 'apps-service', status: 'degraded', latency: 120, cpu: 78, memory: 85, requests: 9200 },
    { name: 'phones-service', status: 'healthy', latency: 38, cpu: 18, memory: 35, requests: 4100 },
    { name: 'local-ai', status: 'healthy', latency: 250, cpu: 65, memory: 72, requests: 3800 },
  ],

  agents: [
    { id: 'outcome.plan_generation.v1', name: 'Plan Generation', engine: 'Outcome', type: 'ambassador', status: 'active', executions: 1250, avgTime: 450 },
    { id: 'outcome.evaluation.v1', name: 'Outcome Evaluation', engine: 'Outcome', type: 'operator', status: 'active', executions: 3400, avgTime: 120 },
    { id: 'rights.consent_scope.v1', name: 'Consent & Scope', engine: 'Rights & Trust', type: 'assistant', status: 'active', executions: 890, avgTime: 85 },
    { id: 'rights.dispute_advocacy.v1', name: 'Dispute Advocacy', engine: 'Rights & Trust', type: 'ambassador', status: 'active', executions: 456, avgTime: 680 },
    { id: 'risk.threat_intel.v1', name: 'Threat Intelligence', engine: 'Risk & Security', type: 'operator', status: 'active', executions: 8900, avgTime: 35 },
    { id: 'risk.incident_response.v1', name: 'Incident Response', engine: 'Risk & Security', type: 'ambassador', status: 'active', executions: 23, avgTime: 1200 },
    { id: 'market.underwriting_decision.v1', name: 'Underwriting Decision', engine: 'Market & Capital', type: 'ambassador', status: 'active', executions: 2100, avgTime: 380 },
    { id: 'market.portfolio_analysis.v1', name: 'Portfolio Analysis', engine: 'Market & Capital', type: 'operator', status: 'active', executions: 560, avgTime: 520 },
    { id: 'cross.explainer.v1', name: 'Explainer', engine: 'Cross-cutting', type: 'assistant', status: 'active', executions: 15600, avgTime: 180 },
    { id: 'cross.notification.v1', name: 'Notification', engine: 'Cross-cutting', type: 'ambassador', status: 'active', executions: 28400, avgTime: 45 },
  ],

  hitlQueue: [
    { id: 'HITL-001', agent: 'Underwriting Decision', task: 'High-value loan approval', risk: 'high', consumer: 'Alice Brown', amount: 150000, waitTime: 15 },
    { id: 'HITL-002', agent: 'Rights Request Orchestrator', task: 'Bulk data deletion', risk: 'high', consumer: 'Data Export Request', amount: null, waitTime: 45 },
    { id: 'HITL-003', agent: 'Security Remediation', task: 'Endpoint isolation', risk: 'critical', consumer: 'WORKSTATION-42', amount: null, waitTime: 5 },
    { id: 'HITL-004', agent: 'Dispute Advocacy', task: 'Bureau letter approval', risk: 'high', consumer: 'Michael Chen', amount: null, waitTime: 120 },
    { id: 'HITL-005', agent: 'Capital Allocation', task: 'Large capital rebalance', risk: 'high', consumer: 'Apex Lending', amount: 5000000, waitTime: 30 },
  ],

  auditLogs: [
    { id: 'AUD-001', action: 'agent_execution', agent: 'Plan Generation', user: 'system', timestamp: '2026-01-16T12:15:00Z', status: 'success' },
    { id: 'AUD-002', action: 'hitl_approval', agent: 'Underwriting Decision', user: 'admin@creditx.ai', timestamp: '2026-01-16T11:45:00Z', status: 'approved' },
    { id: 'AUD-003', action: 'data_export', agent: 'Rights Request', user: 'consumer_001', timestamp: '2026-01-16T10:30:00Z', status: 'completed' },
    { id: 'AUD-004', action: 'threat_detected', agent: 'Threat Intel', user: 'system', timestamp: '2026-01-16T09:15:00Z', status: 'escalated' },
    { id: 'AUD-005', action: 'login', agent: null, user: 'partner@apex.com', timestamp: '2026-01-16T08:00:00Z', status: 'success' },
  ],

  tenants: [
    { id: 'tenant_001', name: 'Nuvei', domain: 'nuvei.ecosystem.ai', modules: ['creditx', '91apps', 'guardian'], users: 45, status: 'active' },
    { id: 'tenant_002', name: 'Apex Lending', domain: 'apex.ecosystem.ai', modules: ['creditx', 'market'], users: 28, status: 'active' },
    { id: 'tenant_003', name: 'SecureNet', domain: 'securenet.ecosystem.ai', modules: ['guardian', 'global-ai-alert'], users: 15, status: 'active' },
    { id: 'tenant_004', name: 'FinTrack', domain: 'fintrack.ecosystem.ai', modules: ['creditx', '91apps'], users: 32, status: 'trial' },
  ],

  threats: [
    { id: 'THR-001', type: 'c2_beacon', severity: 'high', source: '192.168.1.105', status: 'investigating', detected: '2026-01-16T11:30:00Z' },
    { id: 'THR-002', type: 'port_scan', severity: 'medium', source: '10.0.0.88', status: 'blocked', detected: '2026-01-16T10:15:00Z' },
    { id: 'THR-003', type: 'brute_force', severity: 'high', source: '203.0.113.42', status: 'blocked', detected: '2026-01-16T08:45:00Z' },
  ],
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    notation: value >= 1000000 ? 'compact' : 'standard',
    maximumFractionDigits: value >= 1000000 ? 1 : 0,
  }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(date: string): string {
  return new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getScoreColor(score: number): string {
  if (score >= 740) return 'text-emerald-600';
  if (score >= 670) return 'text-blue-600';
  if (score >= 580) return 'text-amber-600';
  return 'text-red-600';
}

export function getScoreLabel(score: number): string {
  if (score >= 800) return 'Exceptional';
  if (score >= 740) return 'Very Good';
  if (score >= 670) return 'Good';
  if (score >= 580) return 'Fair';
  return 'Poor';
}
