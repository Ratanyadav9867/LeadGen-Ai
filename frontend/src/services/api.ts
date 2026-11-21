import type { HealthStatus, Lead, LeadStats, IntegrationItem, EmailRecord } from '../types';
import { DEMO_LEADS, DEMO_INTEGRATIONS, DEMO_EMAILS } from '../data/demoLeads';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(): Promise<HealthStatus> {
  const startTime = performance.now();
  const url = `${API_BASE_URL}/api/health`;

  try {
    const res = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
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

export interface LeadsResult {
  leads: Lead[];
  isDemo: boolean;
  total: number;
}

export async function fetchLeads(filters?: { priority?: string; email_status?: string; search?: string }): Promise<LeadsResult> {
  try {
    const params = new URLSearchParams();
    if (filters?.priority && filters.priority !== 'All') params.append('priority', filters.priority);
    if (filters?.email_status && filters.email_status !== 'All') params.append('email_status', filters.email_status);
    if (filters?.search) params.append('search', filters.search);

    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE_URL}/api/leads${qs}`, {
      headers: { 'Accept': 'application/json' },
    });

    if (res.ok) {
      const liveData: Lead[] = await res.json();
      if (liveData.length > 0) {
        return { leads: liveData, isDemo: false, total: liveData.length };
      }
    }
  } catch (e) {
    // Fall back to explicitly labeled demo dataset
  }

  // Filter demo leads client-side
  let filtered = [...DEMO_LEADS];
  if (filters?.priority && filters.priority !== 'All') {
    filtered = filtered.filter(l => l.priority.toLowerCase() === filters.priority?.toLowerCase());
  }
  if (filters?.email_status && filters.email_status !== 'All') {
    filtered = filtered.filter(l => l.email_status.toLowerCase() === filters.email_status?.toLowerCase());
  }
  if (filters?.search) {
    const query = filters.search.toLowerCase();
    filtered = filtered.filter(l =>
      l.name.toLowerCase().includes(query) ||
      l.company.toLowerCase().includes(query) ||
      l.email.toLowerCase().includes(query) ||
      l.service.toLowerCase().includes(query)
    );
  }

  return { leads: filtered, isDemo: true, total: filtered.length };
}

export async function fetchStats(): Promise<{ stats: LeadStats; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/leads/stats`, {
      headers: { 'Accept': 'application/json' },
    });
    if (res.ok) {
      const stats: LeadStats = await res.json();
      if (stats.total_leads > 0) {
        return { stats, isDemo: false };
      }
    }
  } catch (e) {
    // Fall back
  }

  return {
    stats: {
      total_leads: DEMO_LEADS.length,
      new_leads: DEMO_LEADS.filter(l => l.email_status === 'Pending').length,
      high_priority_leads: DEMO_LEADS.filter(l => l.priority === 'High').length,
      emails_sent: DEMO_LEADS.filter(l => l.email_status === 'Sent').length,
      emails_failed: DEMO_LEADS.filter(l => l.email_status === 'Failed').length,
    },
    isDemo: true,
  };
}

export async function createLead(leadData: Omit<Lead, 'id' | 'created_at' | 'processed_at'>): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/api/leads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(leadData),
  });

  if (!res.ok) {
    throw new Error(`Failed to create lead: ${res.statusText}`);
  }

  return await res.json();
}

export async function fetchIntegrations(): Promise<IntegrationItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/integrations/status`, {
      headers: { 'Accept': 'application/json' },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Fall back
  }
  return DEMO_INTEGRATIONS;
}

export async function fetchEmails(): Promise<EmailRecord[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/integrations/emails`, {
      headers: { 'Accept': 'application/json' },
    });
    if (res.ok) {
      const data: EmailRecord[] = await res.json();
      if (data.length > 0) {
        return data;
      }
    }
  } catch (e) {
    // Fall back
  }
  return DEMO_EMAILS;
}

export async function generateAIEmail(leadId: number): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${leadId}/generate-ai`, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`Failed to generate AI response: ${res.statusText}`);
  }

  return await res.json();
}

export async function updateLeadStatus(leadId: number, status: { email_status?: string; priority?: string }): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${leadId}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(status),
  });

  if (!res.ok) {
    throw new Error(`Failed to update status: ${res.statusText}`);
  }

  return await res.json();
}

export async function sendTestWebhook(payload: {
  name: string;
  company: string;
  email: string;
  service: string;
  budget: string;
  description: string;
}): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE_URL}/api/automation/webhook`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Webhook failed: ${res.statusText}`);
  }

  return await res.json();
}

export async function sendLeadEmail(leadId: number): Promise<{
  success: boolean;
  lead_id: number;
  recipient: string;
  subject: string;
  email_status: string;
  gmail_message_id?: string | null;
  error_message?: string | null;
}> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${leadId}/send-email`, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to dispatch email: ${res.statusText}`);
  }

  return await res.json();
}

export async function checkSendEligibility(leadId: number): Promise<{
  lead_id: number;
  eligible: boolean;
  reason?: string | null;
  recipient: string;
  email_status: string;
  has_draft: boolean;
  subject?: string | null;
  body?: string | null;
}> {
  const res = await fetch(`${API_BASE_URL}/api/leads/${leadId}/send-eligibility`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`Failed to check eligibility: ${res.statusText}`);
  }

  return await res.json();
}


