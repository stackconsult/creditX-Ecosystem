import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { defaultLogger } from './logger';

export interface ServiceClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export function createServiceClient(config: ServiceClientConfig): AxiosInstance {
  const client = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout || 30000,
    headers: {
      'Content-Type': 'application/json',
      ...config.headers,
    },
  });

  client.interceptors.request.use((req) => {
    defaultLogger.debug({ url: req.url, method: req.method }, 'Outgoing request');
    return req;
  });

  client.interceptors.response.use(
    (res) => {
      defaultLogger.debug({ url: res.config.url, status: res.status }, 'Response received');
      return res;
    },
    (error) => {
      defaultLogger.error({
        url: error.config?.url,
        status: error.response?.status,
        message: error.message,
      }, 'Request failed');
      throw error;
    }
  );

  return client;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delayMs = 1000
): Promise<T> {
  let lastError: Error | undefined;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs * (i + 1)));
      }
    }
  }
  
  throw lastError;
}
