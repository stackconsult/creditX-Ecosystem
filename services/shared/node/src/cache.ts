import Redis from 'ioredis';

export interface CacheConfig {
  host: string;
  port: number;
  password?: string;
  keyPrefix?: string;
}

export class CacheClient {
  private client: Redis;
  private prefix: string;

  constructor(config: CacheConfig) {
    this.client = new Redis({
      host: config.host,
      port: config.port,
      password: config.password,
      retryStrategy: (times) => Math.min(times * 50, 2000),
    });
    this.prefix = config.keyPrefix || 'creditx:';
  }

  private key(k: string): string {
    return `${this.prefix}${k}`;
  }

  async get<T>(key: string): Promise<T | null> {
    const value = await this.client.get(this.key(key));
    return value ? JSON.parse(value) : null;
  }

  async set(key: string, value: unknown, ttlSeconds = 3600): Promise<void> {
    await this.client.setex(this.key(key), ttlSeconds, JSON.stringify(value));
  }

  async del(key: string): Promise<void> {
    await this.client.del(this.key(key));
  }

  async exists(key: string): Promise<boolean> {
    return (await this.client.exists(this.key(key))) === 1;
  }

  async close(): Promise<void> {
    await this.client.quit();
  }
}

export function createCacheClient(): CacheClient {
  return new CacheClient({
    host: process.env.DRAGONFLY_HOST || 'localhost',
    port: parseInt(process.env.DRAGONFLY_PORT || '6379', 10),
    password: process.env.DRAGONFLY_PASSWORD,
  });
}
