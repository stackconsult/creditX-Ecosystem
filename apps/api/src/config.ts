import dotenv from 'dotenv';
dotenv.config();

export const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '4000', 10),
  
  corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  
  services: {
    creditx: process.env.CREDITX_SERVICE_URL || 'http://localhost:8000',
    threat: process.env.THREAT_SERVICE_URL || 'http://localhost:8001',
    guardian: process.env.GUARDIAN_SERVICE_URL || 'http://localhost:8002',
    apps: process.env.APPS_SERVICE_URL || 'http://localhost:8003',
    phones: process.env.PHONES_SERVICE_URL || 'http://localhost:8004',
    agent: process.env.AGENT_SERVICE_URL || 'http://localhost:8010',
  },
  
  cache: {
    host: process.env.DRAGONFLY_HOST || 'localhost',
    port: parseInt(process.env.DRAGONFLY_PORT || '6379', 10),
    password: process.env.DRAGONFLY_PASSWORD || undefined,
  },
  
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
    max: parseInt(process.env.RATE_LIMIT_MAX || '1000', 10),
  },
};
