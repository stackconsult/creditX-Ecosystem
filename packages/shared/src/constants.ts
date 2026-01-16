export const API_VERSION = 'v1';

export const FACES = ['consumer', 'partner', 'internal'] as const;

export const AGENT_ENGINES = ['outcome', 'rights_trust', 'risk_security', 'market_capital'] as const;

export const RISK_LEVELS = ['low', 'medium', 'high', 'critical'] as const;

export const CREDIT_BUREAUS = ['equifax', 'experian', 'transunion'] as const;

export const HITL_TIMEOUT_MS = 3600000;

export const MAX_AGENT_ITERATIONS = 10;

export const RATE_LIMITS = {
  consumer: { requests: 100, windowMs: 60000 },
  partner: { requests: 500, windowMs: 60000 },
  internal: { requests: 1000, windowMs: 60000 },
} as const;

export const SCORE_RANGES = {
  poor: { min: 300, max: 579 },
  fair: { min: 580, max: 669 },
  good: { min: 670, max: 739 },
  veryGood: { min: 740, max: 799 },
  excellent: { min: 800, max: 850 },
} as const;

export const COMPLIANCE_REGULATIONS = [
  'FCRA',
  'ECOA',
  'TILA',
  'RESPA',
  'FDCPA',
  'CCPA',
  'GDPR',
] as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
} as const;

export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_REQUIRED: 'AUTHENTICATION_REQUIRED',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  SERVICE_ERROR: 'SERVICE_ERROR',
  HITL_REQUIRED: 'HITL_REQUIRED',
  AGENT_ERROR: 'AGENT_ERROR',
} as const;
