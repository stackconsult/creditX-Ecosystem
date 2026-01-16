import { SCORE_RANGES } from './constants';
import type { RiskLevel } from './types';

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function formatPercentage(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', options || { dateStyle: 'medium' });
}

export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
}

export function getScoreLabel(score: number): string {
  if (score >= SCORE_RANGES.excellent.min) return 'Excellent';
  if (score >= SCORE_RANGES.veryGood.min) return 'Very Good';
  if (score >= SCORE_RANGES.good.min) return 'Good';
  if (score >= SCORE_RANGES.fair.min) return 'Fair';
  return 'Poor';
}

export function getScoreColor(score: number): string {
  if (score >= SCORE_RANGES.excellent.min) return 'text-emerald-600';
  if (score >= SCORE_RANGES.veryGood.min) return 'text-green-600';
  if (score >= SCORE_RANGES.good.min) return 'text-blue-600';
  if (score >= SCORE_RANGES.fair.min) return 'text-yellow-600';
  return 'text-red-600';
}

export function getRiskColor(risk: RiskLevel): string {
  switch (risk) {
    case 'low': return 'text-green-600 bg-green-50';
    case 'medium': return 'text-yellow-600 bg-yellow-50';
    case 'high': return 'text-orange-600 bg-orange-50';
    case 'critical': return 'text-red-600 bg-red-50';
    default: return 'text-gray-600 bg-gray-50';
  }
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function generateId(prefix = ''): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return prefix ? `${prefix}_${timestamp}${random}` : `${timestamp}${random}`;
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}

export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((groups, item) => {
    const groupKey = String(item[key]);
    if (!groups[groupKey]) groups[groupKey] = [];
    groups[groupKey].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

export function pick<T extends object, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    if (key in obj) result[key] = obj[key];
  });
  return result;
}

export function omit<T extends object, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> {
  const result = { ...obj };
  keys.forEach(key => delete result[key]);
  return result;
}
