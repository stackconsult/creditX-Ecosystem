import { Request, Response, NextFunction } from 'express';
import { defaultLogger } from './logger';

export interface TenantContext {
  tenantId: string;
  face: 'consumer' | 'partner' | 'internal';
  userId?: string;
}

declare global {
  namespace Express {
    interface Request {
      tenant?: TenantContext;
    }
  }
}

export function tenantMiddleware(req: Request, res: Response, next: NextFunction) {
  req.tenant = {
    tenantId: req.get('x-tenant-id') || 'default',
    face: (req.get('x-face') as TenantContext['face']) || 'internal',
    userId: req.get('x-user-id'),
  };
  next();
}

export function requestLoggerMiddleware(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  
  res.on('finish', () => {
    defaultLogger.info({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: Date.now() - start,
      tenantId: req.tenant?.tenantId,
    }, 'Request completed');
  });
  
  next();
}

export function errorMiddleware(err: Error, req: Request, res: Response, _next: NextFunction) {
  defaultLogger.error({ err, path: req.path }, 'Unhandled error');
  
  res.status(500).json({
    error: {
      message: process.env.NODE_ENV === 'production' 
        ? 'Internal server error' 
        : err.message,
      code: 'INTERNAL_ERROR',
    },
  });
}
