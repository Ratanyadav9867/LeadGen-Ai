export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'down';
  service: string;
  version: string;
  environment: string;
  database: string;
  latencyMs?: number;
  timestamp?: string;
}

export type PriorityLevel = 'High' | 'Medium' | 'Low';
export type EmailDeliveryStatus = 'Pending' | 'Draft' | 'Sent' | 'Failed';


export interface Lead {
  id: number;
  name: string;
  company: string;
  email: string;
  phone?: string | null;
  service: string;
  budget: string;
  description?: string | null;
  priority: PriorityLevel;
  priority_reason?: string | null;
  email_status: EmailDeliveryStatus;
  email_subject?: string | null;
  email_body?: string | null;
  created_at: string;
  processed_at?: string | null;
}

export interface LeadStats {
  total_leads: number;
  new_leads: number;
  high_priority_leads: number;
  emails_sent: number;
  emails_failed: number;
}

export type IntegrationStatus = 'Connected' | 'Not configured' | 'Error';

export interface IntegrationItem {
  id: string;
  name: string;
  category: string;
  status: IntegrationStatus;
  details: string;
  workflow_step: number;
}

export interface EmailRecord {
  id: number;
  lead_name: string;
  company: string;
  recipient: string;
  subject: string;
  body: string;
  status: EmailDeliveryStatus;
  timestamp: string;
  priority: PriorityLevel;
}
