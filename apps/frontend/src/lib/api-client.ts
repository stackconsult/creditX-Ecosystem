/**
 * CreditX API Client
 * Centralized API wrapper with tenant/face headers
 * Connects to API Gateway which routes to backend services
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
const AGENT_BASE = process.env.NEXT_PUBLIC_AGENT_URL || 'http://localhost:8010';

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  tenantId?: string;
  face?: 'consumer' | 'partner' | 'internal';
}

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

export async function apiClient<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<ApiResponse<T>> {
  const {
    method = 'GET',
    body,
    headers = {},
    tenantId = 'default',
    face = 'internal',
  } = options;

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  try {
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
        'X-Face': face,
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      return {
        data: null,
        error: data?.detail || data?.message || `Error ${response.status}`,
        status: response.status,
      };
    }

    return { data, error: null, status: response.status };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }
}

export const api = {
  get: <T>(endpoint: string, options?: Omit<ApiOptions, 'method'>) =>
    apiClient<T>(endpoint, { ...options, method: 'GET' }),
  
  post: <T>(endpoint: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    apiClient<T>(endpoint, { ...options, method: 'POST', body }),
  
  put: <T>(endpoint: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    apiClient<T>(endpoint, { ...options, method: 'PUT', body }),
  
  patch: <T>(endpoint: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    apiClient<T>(endpoint, { ...options, method: 'PATCH', body }),
  
  delete: <T>(endpoint: string, options?: Omit<ApiOptions, 'method'>) =>
    apiClient<T>(endpoint, { ...options, method: 'DELETE' }),
};

export const consumerApi = {
  getCreditReport: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/consumer/credit-report', { ...options, face: 'consumer' }),
  getCreditScore: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/consumer/credit-score', { ...options, face: 'consumer' }),
  getDisputes: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/consumer/disputes', { ...options, face: 'consumer' }),
  createDispute: (body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post('/api/v1/consumer/disputes', body, { ...options, face: 'consumer' }),
  getPlans: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/consumer/plans', { ...options, face: 'consumer' }),
  getDataRights: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/consumer/data-rights', { ...options, face: 'consumer' }),
};

export const partnerApi = {
  getPortfolio: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/partner/portfolio', { ...options, face: 'partner' }),
  getLoans: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/partner/portfolio/loans', { ...options, face: 'partner' }),
  getUnderwritingQueue: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/partner/underwriting/queue', { ...options, face: 'partner' }),
  approveApplication: (applicationId: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post(`/api/v1/partner/underwriting/${applicationId}/approve`, body, { ...options, face: 'partner' }),
  declineApplication: (applicationId: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post(`/api/v1/partner/underwriting/${applicationId}/decline`, body, { ...options, face: 'partner' }),
  getAnalytics: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/partner/analytics', { ...options, face: 'partner' }),
  getCompliance: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/partner/compliance', { ...options, face: 'partner' }),
};

export const internalApi = {
  getSystemStats: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/internal/system/stats', { ...options, face: 'internal' }),
  getServices: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/internal/services', { ...options, face: 'internal' }),
  getHitlQueue: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/internal/hitl/queue', { ...options, face: 'internal' }),
  approveHitl: (requestId: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post(`/api/v1/internal/hitl/${requestId}/approve`, body, { ...options, face: 'internal' }),
  rejectHitl: (requestId: string, body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post(`/api/v1/internal/hitl/${requestId}/reject`, body, { ...options, face: 'internal' }),
  getAuditLogs: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/internal/audit/logs', { ...options, face: 'internal' }),
  getTenants: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/internal/tenants', { ...options, face: 'internal' }),
};

export const agentApi = {
  listAgents: (options?: Omit<ApiOptions, 'method'>) =>
    api.get('/api/v1/agents', options),
  getAgent: (agentId: string, options?: Omit<ApiOptions, 'method'>) =>
    api.get(`/api/v1/agents/${agentId}`, options),
  executeAgent: (body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post('/api/v1/agents/execute', body, options),
  chat: (body: unknown, options?: Omit<ApiOptions, 'method' | 'body'>) =>
    api.post('/api/v1/agents/chat', body, options),
};

export { AGENT_BASE };
export default api;
