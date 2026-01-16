import axios, { AxiosInstance, AxiosError } from 'axios';
import { config } from '../config';
import { logger } from './logger';

type ServiceName = keyof typeof config.services;

const clients: Map<ServiceName, AxiosInstance> = new Map();

export function getServiceClient(service: ServiceName): AxiosInstance {
  if (!clients.has(service)) {
    const baseURL = config.services[service];
    const client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    client.interceptors.request.use((req) => {
      logger.debug({ service, method: req.method, url: req.url }, 'Service request');
      return req;
    });

    client.interceptors.response.use(
      (res) => {
        logger.debug({ service, status: res.status }, 'Service response');
        return res;
      },
      (error: AxiosError) => {
        logger.error({
          service,
          status: error.response?.status,
          message: error.message,
        }, 'Service error');
        throw error;
      }
    );

    clients.set(service, client);
  }
  return clients.get(service)!;
}

export async function forwardRequest(
  service: ServiceName,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  path: string,
  data?: unknown,
  headers?: Record<string, string>
) {
  const client = getServiceClient(service);
  const response = await client.request({
    method,
    url: path,
    data,
    headers,
  });
  return response.data;
}
