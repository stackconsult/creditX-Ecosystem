import { Router } from 'express';
import bcrypt from 'bcryptjs';
import { generateToken, authMiddleware, AuthenticatedRequest } from '../middleware/auth';
import { logger } from '../lib/logger';
import { forwardRequest } from '../lib/service-client';

const router = Router();

interface LoginRequest {
  email: string;
  password: string;
  tenantId?: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  tenantId: string;
  face?: 'consumer' | 'partner' | 'internal';
  profile?: Record<string, unknown>;
}

router.post('/login', async (req, res, next) => {
  try {
    const { email, password, tenantId = 'default' }: LoginRequest = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: 'Email and password required',
        code: 'MISSING_CREDENTIALS',
      });
    }

    // In production, validate against database via creditx-service
    // For MVP, use a simple validation
    try {
      const user = await forwardRequest('creditx', 'POST', '/api/v1/auth/validate', {
        email,
        password,
        tenantId,
      });

      const token = generateToken({
        userId: user.id,
        tenantId: user.tenantId || tenantId,
        email: user.email,
        role: user.role || 'user',
        face: user.face || 'consumer',
      });

      logger.info('User login successful', { email, tenantId });

      return res.json({
        token,
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          face: user.face,
          profile: user.profile,
        },
        expiresIn: '24h',
      });
    } catch (serviceError) {
      // Fallback for development - accept any login
      if (process.env.NODE_ENV === 'development') {
        const devToken = generateToken({
          userId: 'dev-user-001',
          tenantId,
          email,
          role: 'admin',
          face: 'internal',
        });

        logger.warn('Development mode: bypassing auth validation', { email });

        return res.json({
          token: devToken,
          user: {
            id: 'dev-user-001',
            email,
            role: 'admin',
            face: 'internal',
          },
          expiresIn: '24h',
          warning: 'Development mode - auth validation bypassed',
        });
      }

      throw serviceError;
    }
  } catch (error) {
    logger.error('Login failed', { error: (error as Error).message });
    return res.status(401).json({
      error: 'Invalid credentials',
      code: 'INVALID_CREDENTIALS',
    });
  }
});

router.post('/register', async (req, res, next) => {
  try {
    const { email, password, tenantId, face = 'consumer', profile = {} }: RegisterRequest = req.body;

    if (!email || !password || !tenantId) {
      return res.status(400).json({
        error: 'Email, password, and tenantId required',
        code: 'MISSING_FIELDS',
      });
    }

    if (password.length < 8) {
      return res.status(400).json({
        error: 'Password must be at least 8 characters',
        code: 'WEAK_PASSWORD',
      });
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 12);

    // Create user via creditx-service
    try {
      const user = await forwardRequest('creditx', 'POST', '/api/v1/auth/register', {
        email,
        passwordHash,
        tenantId,
        face,
        profile,
      });

      const token = generateToken({
        userId: user.id,
        tenantId: user.tenantId,
        email: user.email,
        role: user.role || 'user',
        face: user.face || face,
      });

      logger.info('User registered', { email, tenantId, face });

      return res.status(201).json({
        token,
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          face: user.face,
        },
      });
    } catch (serviceError) {
      // Development fallback
      if (process.env.NODE_ENV === 'development') {
        const devToken = generateToken({
          userId: `dev-${Date.now()}`,
          tenantId,
          email,
          role: 'user',
          face,
        });

        return res.status(201).json({
          token: devToken,
          user: {
            id: `dev-${Date.now()}`,
            email,
            role: 'user',
            face,
          },
          warning: 'Development mode - user not persisted',
        });
      }

      throw serviceError;
    }
  } catch (error) {
    logger.error('Registration failed', { error: (error as Error).message });
    return res.status(500).json({
      error: 'Registration failed',
      code: 'REGISTRATION_FAILED',
    });
  }
});

router.post('/refresh', authMiddleware, async (req: AuthenticatedRequest, res) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const token = generateToken({
      userId: req.user.userId,
      tenantId: req.user.tenantId,
      email: req.user.email,
      role: req.user.role,
      face: req.user.face,
    });

    return res.json({
      token,
      expiresIn: '24h',
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Token refresh failed',
      code: 'REFRESH_FAILED',
    });
  }
});

router.get('/me', authMiddleware, async (req: AuthenticatedRequest, res) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    return res.json({
      user: {
        id: req.user.userId,
        tenantId: req.user.tenantId,
        email: req.user.email,
        role: req.user.role,
        face: req.user.face,
      },
    });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to get user info' });
  }
});

router.post('/logout', authMiddleware, async (req: AuthenticatedRequest, res) => {
  // In a production system, you'd invalidate the token in a blacklist
  logger.info('User logout', { userId: req.user?.userId });
  return res.json({ message: 'Logged out successfully' });
});

export default router;
