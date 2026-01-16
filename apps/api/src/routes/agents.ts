import { Router } from 'express';
import { forwardRequest } from '../lib/service-client';
import { createError } from '../middleware/error-handler';

const router = Router();

router.get('/', async (req, res, next) => {
  try {
    const data = await forwardRequest('agent', 'GET', '/api/v1/agents', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-face': req.get('x-face') || 'internal',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch agents', 502, 'SERVICE_ERROR'));
  }
});

router.get('/:agentId', async (req, res, next) => {
  try {
    const { agentId } = req.params;
    const data = await forwardRequest('agent', 'GET', `/api/v1/agents/${agentId}`, undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-face': req.get('x-face') || 'internal',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch agent', 502, 'SERVICE_ERROR'));
  }
});

router.post('/execute', async (req, res, next) => {
  try {
    const data = await forwardRequest('agent', 'POST', '/api/v1/agents/execute', req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-face': req.get('x-face') || 'internal',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to execute agent', 502, 'SERVICE_ERROR'));
  }
});

router.post('/chat', async (req, res, next) => {
  try {
    const data = await forwardRequest('agent', 'POST', '/api/v1/agents/chat', req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-face': req.get('x-face') || 'internal',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to process chat', 502, 'SERVICE_ERROR'));
  }
});

router.get('/executions', async (req, res, next) => {
  try {
    const data = await forwardRequest('agent', 'GET', '/api/v1/agents/executions', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch executions', 502, 'SERVICE_ERROR'));
  }
});

router.get('/executions/:executionId', async (req, res, next) => {
  try {
    const { executionId } = req.params;
    const data = await forwardRequest('agent', 'GET', `/api/v1/agents/executions/${executionId}`, undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch execution', 502, 'SERVICE_ERROR'));
  }
});

export default router;
