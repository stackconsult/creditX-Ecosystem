import { z } from 'zod';

export const FaceSchema = z.enum(['consumer', 'partner', 'internal']);

export const AgentEngineSchema = z.enum(['outcome', 'rights_trust', 'risk_security', 'market_capital']);

export const RiskLevelSchema = z.enum(['low', 'medium', 'high', 'critical']);

export const TenantContextSchema = z.object({
  tenantId: z.string().min(1),
  face: FaceSchema,
  userId: z.string().optional(),
  consumerId: z.string().optional(),
  partnerId: z.string().optional(),
});

export const ExecuteAgentRequestSchema = z.object({
  agentId: z.string().min(1),
  action: z.string().min(1),
  parameters: z.record(z.unknown()).default({}),
  context: z.record(z.unknown()).default({}),
});

export const ChatMessageSchema = z.object({
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
});

export const ChatRequestSchema = z.object({
  messages: z.array(ChatMessageSchema).min(1),
  context: z.record(z.unknown()).optional(),
  agentId: z.string().optional(),
});

export const DisputeRequestSchema = z.object({
  item: z.string().min(1),
  reason: z.string().min(10),
  bureau: z.enum(['equifax', 'experian', 'transunion']).optional(),
  evidence: z.array(z.string()).optional(),
});

export const UnderwritingDecisionSchema = z.object({
  applicationId: z.string().min(1),
  decision: z.enum(['approve', 'decline', 'manual_review']),
  reason: z.string().optional(),
  terms: z.object({
    amount: z.number().positive(),
    apr: z.number().min(0).max(100),
    term: z.number().positive(),
  }).optional(),
});

export const HitlResolutionSchema = z.object({
  requestId: z.string().min(1),
  action: z.enum(['approve', 'reject']),
  reason: z.string().optional(),
  modifiedPayload: z.record(z.unknown()).optional(),
});

export const DataRightsRequestSchema = z.object({
  type: z.enum(['export', 'delete', 'restrict', 'portability']),
  scope: z.enum(['all', 'credit', 'disputes', 'plans']).default('all'),
  format: z.enum(['json', 'csv', 'pdf']).optional(),
});
