import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { config } from './config';
import { logger } from './lib/logger';
import { errorHandler } from './middleware/error-handler';
import { requestLogger } from './middleware/request-logger';

import consumerRoutes from './routes/consumer';
import partnerRoutes from './routes/partner';
import internalRoutes from './routes/internal';
import agentRoutes from './routes/agents';
import healthRoutes from './routes/health';

const app = express();

app.use(helmet());
app.use(cors({
  origin: config.corsOrigins,
  credentials: true,
}));
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' },
});
app.use(limiter);

app.use(requestLogger);

app.use('/health', healthRoutes);
app.use('/api/v1/consumer', consumerRoutes);
app.use('/api/v1/partner', partnerRoutes);
app.use('/api/v1/internal', internalRoutes);
app.use('/api/v1/agents', agentRoutes);

app.use(errorHandler);

app.listen(config.port, () => {
  logger.info(`API Gateway running on port ${config.port}`);
  logger.info(`Environment: ${config.env}`);
});

export default app;
