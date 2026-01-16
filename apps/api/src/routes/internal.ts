import { Router } from 'express';
import { forwardRequest } from '../lib/service-client';
import { createError } from '../middleware/error-handler';

const router = Router();

router.get('/system/stats', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/internal/system/stats', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch system stats', 502, 'SERVICE_ERROR'));
  }
});

router.get('/services', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/internal/services', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch services', 502, 'SERVICE_ERROR'));
  }
});

router.get('/hitl/queue', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/agents/hitl/pending', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch HITL queue', 502, 'SERVICE_ERROR'));
  }
});

router.post('/hitl/:requestId/approve', async (req, res, next) => {
  try {
    const { requestId } = req.params;
    const data = await forwardRequest('creditx', 'POST', `/api/v1/agents/hitl/${requestId}/approve`, req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to approve HITL request', 502, 'SERVICE_ERROR'));
  }
});

router.post('/hitl/:requestId/reject', async (req, res, next) => {
  try {
    const { requestId } = req.params;
    const data = await forwardRequest('creditx', 'POST', `/api/v1/agents/hitl/${requestId}/reject`, req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to reject HITL request', 502, 'SERVICE_ERROR'));
  }
});

router.get('/audit/logs', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/internal/audit/logs', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch audit logs', 502, 'SERVICE_ERROR'));
  }
});

router.get('/tenants', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/internal/tenants', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch tenants', 502, 'SERVICE_ERROR'));
  }
});

router.get('/tenants/:tenantId', async (req, res, next) => {
  try {
    const { tenantId } = req.params;
    const data = await forwardRequest('creditx', 'GET', `/api/v1/internal/tenants/${tenantId}`, undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch tenant', 502, 'SERVICE_ERROR'));
  }
});

export default router;
