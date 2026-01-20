import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { logger } from '../lib/logger';
import { config } from '../config';

export interface JWTPayload {
  userId: string;
  tenantId: string;
  email: string;
  role: 'admin' | 'manager' | 'user' | 'viewer';
  face: 'consumer' | 'partner' | 'internal';
  iat?: number;
  exp?: number;
}

export interface AuthenticatedRequest extends Request {
  user?: JWTPayload;
}

const JWT_SECRET = process.env.JWT_SECRET || 'creditx-dev-secret-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

export function generateToken(payload: Omit<JWTPayload, 'iat' | 'exp'>): string {
  // Use any to bypass TypeScript overload issues
  return (jwt.sign as any)(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

export function verifyToken(token: string): JWTPayload {
  return jwt.verify(token, JWT_SECRET) as JWTPayload;
}

export function authMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  const apiKey = req.headers['x-api-key'] as string;

  // Try Bearer token first
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    
    try {
      const payload = verifyToken(token);
      req.user = payload;
      
      // Set tenant context headers for downstream services
      req.headers['x-tenant-id'] = payload.tenantId;
      req.headers['x-user-id'] = payload.userId;
      req.headers['x-user-role'] = payload.role;
      req.headers['x-face'] = payload.face;
      
      return next();
    } catch (error) {
      logger.warn('Invalid JWT token', { error: (error as Error).message });
      return res.status(401).json({
        error: 'Invalid or expired token',
        code: 'INVALID_TOKEN',
      });
    }
  }

  // Try API key
  if (apiKey) {
    // In production, validate against database
    // For now, accept format: ck_<tenantId>_<key>
    if (apiKey.startsWith('ck_')) {
      const parts = apiKey.split('_');
      if (parts.length >= 3) {
        req.user = {
          userId: 'api-key-user',
          tenantId: parts[1],
          email: 'api@creditx.ai',
          role: 'user',
          face: 'internal',
        };
        req.headers['x-tenant-id'] = parts[1];
        return next();
      }
    }
    
    return res.status(401).json({
      error: 'Invalid API key',
      code: 'INVALID_API_KEY',
    });
  }

  return res.status(401).json({
    error: 'Authentication required',
    code: 'AUTH_REQUIRED',
  });
}

export function optionalAuth(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    
    try {
      const payload = verifyToken(token);
      req.user = payload;
      req.headers['x-tenant-id'] = payload.tenantId;
      req.headers['x-user-id'] = payload.userId;
    } catch {
      // Token invalid, but continue without auth
    }
  }

  next();
}

export function requireRole(...roles: JWTPayload['role'][]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        code: 'AUTH_REQUIRED',
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        code: 'FORBIDDEN',
        required: roles,
        current: req.user.role,
      });
    }

    next();
  };
}

export function requireFace(...faces: JWTPayload['face'][]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required',
        code: 'AUTH_REQUIRED',
      });
    }

    if (!faces.includes(req.user.face)) {
      return res.status(403).json({
        error: 'Access denied for this interface',
        code: 'FACE_FORBIDDEN',
        required: faces,
        current: req.user.face,
      });
    }

    next();
  };
}
