export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'down';
  service: string;
  version: string;
  environment: string;
  database: string;
  latencyMs?: number;
  timestamp?: string;
}

