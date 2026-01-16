import { Router } from 'express';
import { getServiceClient } from '../lib/service-client';
import { config } from '../config';

const router = Router();

router.get('/live', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

router.get('/ready', async (req, res) => {
  const checks: Record<string, { status: string; latency?: number }> = {};

  const serviceNames = Object.keys(config.services) as Array<keyof typeof config.services>;

  await Promise.all(
    serviceNames.map(async (name) => {
      const start = Date.now();
      try {
        const client = getServiceClient(name);
        await client.get('/health/live', { timeout: 5000 });
        checks[name] = { status: 'healthy', latency: Date.now() - start };
      } catch {
        checks[name] = { status: 'unhealthy', latency: Date.now() - start };
      }
    })
  );

  const allHealthy = Object.values(checks).every((c) => c.status === 'healthy');

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'degraded',
    services: checks,
    timestamp: new Date().toISOString(),
  });
});

export default router;
