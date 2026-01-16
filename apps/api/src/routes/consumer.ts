import { Router } from 'express';
import { forwardRequest } from '../lib/service-client';
import { createError } from '../middleware/error-handler';

const router = Router();

router.get('/credit-report', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/consumer/credit-report', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch credit report', 502, 'SERVICE_ERROR'));
  }
});

router.get('/credit-score', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/consumer/credit-score', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch credit score', 502, 'SERVICE_ERROR'));
  }
});

router.get('/disputes', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/consumer/disputes', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch disputes', 502, 'SERVICE_ERROR'));
  }
});

router.post('/disputes', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'POST', '/api/v1/consumer/disputes', req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.status(201).json(data);
  } catch (error) {
    next(createError('Failed to create dispute', 502, 'SERVICE_ERROR'));
  }
});

router.get('/plans', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/consumer/plans', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch plans', 502, 'SERVICE_ERROR'));
  }
});

router.get('/data-rights', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'GET', '/api/v1/consumer/data-rights', undefined, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.json(data);
  } catch (error) {
    next(createError('Failed to fetch data rights', 502, 'SERVICE_ERROR'));
  }
});

router.post('/data-rights/request', async (req, res, next) => {
  try {
    const data = await forwardRequest('creditx', 'POST', '/api/v1/consumer/data-rights/request', req.body, {
      'x-tenant-id': req.get('x-tenant-id') || 'default',
      'x-consumer-id': req.get('x-consumer-id') || '',
    });
    res.status(201).json(data);
  } catch (error) {
    next(createError('Failed to create data rights request', 502, 'SERVICE_ERROR'));
  }
});

export default router;
