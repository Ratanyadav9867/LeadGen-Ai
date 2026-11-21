import type { HealthStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(): Promise<HealthStatus> {
  const startTime = performance.now();
  const url = `${API_BASE_URL}/api/health`;

  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const latencyMs = Math.round(performance.now() - startTime);

    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    return {
      ...data,
      latencyMs,
      timestamp: new Date().toLocaleTimeString(),
    };
  } catch (error) {
    const latencyMs = Math.round(performance.now() - startTime);
    return {
      status: 'down',
      service: 'LeadGen AI Backend',
      version: 'N/A',
      environment: 'unknown',
      database: 'disconnected',
      latencyMs,
      timestamp: new Date().toLocaleTimeString(),
    };
  }
}
