import pino from 'pino';

export interface LoggerConfig {
  name: string;
  level?: string;
  pretty?: boolean;
}

export function createLogger(config: LoggerConfig) {
  return pino({
    name: config.name,
    level: config.level || process.env.LOG_LEVEL || 'info',
    transport: config.pretty ? {
      target: 'pino-pretty',
      options: { colorize: true },
    } : undefined,
  });
}

export const defaultLogger = createLogger({
  name: 'creditx-service',
  pretty: process.env.NODE_ENV !== 'production',
});
