import { Router } from 'express';
import { forwardRequest } from '../lib/service-client';
import { createError } from '../middleware/error-handler';

const router = Router();

router.get('/portfolio', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/partner/portfolio', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch portfolio', 502, 'SERVICE_ERROR'));
  }
});

router.get('/portfolio/loans', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/partner/portfolio/loans', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch loans', 502, 'SERVICE_ERROR'));
  }
});

router.get('/underwriting/queue', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/partner/underwriting/queue', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch underwriting queue', 502, 'SERVICE_ERROR'));
  }
});

router.post('/underwriting/:applicationId/approve', async (req, res, next) => {
  try {
    const { applicationId } = req.params;
    const data = await forwardRequest('creditx', 'POST', `/api/v1/partner/underwriting/${applicationId}/approve`, req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to approve application', 502, 'SERVICE_ERROR'));
  }
});

router.post('/underwriting/:applicationId/decline', async (req, res, next) => {
  try {
    const { applicationId } = req.params;
    const data = await forwardRequest('creditx', 'POST', `/api/v1/partner/underwriting/${applicationId}/decline`, req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to decline application', 502, 'SERVICE_ERROR'));
  }
});

router.get('/analytics', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/partner/analytics', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch analytics', 502, 'SERVICE_ERROR'));
  }
});

router.get('/compliance', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/compliance/status', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch compliance status', 502, 'SERVICE_ERROR'));
  }
});

router.get('/compliance/fairness', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/compliance/fairness-metrics', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-partner-id': req.get('x-partner-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch fairness metrics', 502, 'SERVICE_ERROR'));
  }
});

export default router;
