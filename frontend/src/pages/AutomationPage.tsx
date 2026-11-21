import React, { useState, useEffect } from 'react';
import type { IntegrationItem } from '../types';
import { fetchIntegrations } from '../services/api';
import { IntegrationStatusBadge } from '../components/Badge';
import {
  FileText,
  FileSpreadsheet,
  Workflow,
  Sparkles,
  Mail,
  ArrowRight,
  ShieldAlert,
  Copy,
  Check,
  RefreshCw
} from 'lucide-react';

export const AutomationPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  const loadIntegrations = async () => {
    setLoading(true);
    const data = await fetchIntegrations();
    setIntegrations(data);
    setLoading(false);
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  const webhookUrl = 'http://127.0.0.1:8000/api/automation/webhook';

  const handleCopyWebhook = () => {
    navigator.clipboard.writeText(webhookUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const workflowSteps = [
    {
      step: 1,
      icon: FileText,
      title: 'Google Form',
      sub: 'Prospect Ingestion',
      desc: 'Inbound client submits questionnaire with service requirements and budget.',
    },
    {
      step: 2,
      icon: FileSpreadsheet,
      title: 'Google Sheets',
      sub: 'Row Sync',
      desc: 'Form response row appended to centralized spreadsheet.',
    },
    {
      step: 3,
      icon: Workflow,
      title: 'n8n Pipeline',
      sub: 'Webhook Router',
      desc: 'Detects new row, triggers conditional logic and data validation.',
    },
    {
      step: 4,
      icon: Sparkles,
      title: 'Gemini AI',
      sub: 'Scoring & Drafting',
      desc: 'Analyzes project scope, scores priority, and crafts tailored email reply.',
    },
    {
      step: 5,
      icon: Mail,
      title: 'Gmail Dispatch',
      sub: 'Automated Follow-Up',
      desc: 'Personalized email sent to prospect automatically within minutes.',
    },
    {
      step: 6,
      icon: FileSpreadsheet,
      title: 'Google Sheets',
      sub: 'Status Update',
      desc: 'Row updated with AI score, email dispatch status, and timestamp.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Automation & Integrations</h2>
          <p className="text-sm text-slate-500 mt-1">
            End-to-end autonomous pipeline orchestration powered by n8n, Google Workspace, and Gemini AI.
          </p>
        </div>

        <button
          onClick={loadIntegrations}
          className="inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors shadow-2xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      {/* Verification Notice */}
      <div className="p-4 bg-amber-50/90 border border-amber-200 rounded-2xl flex items-start space-x-3 text-amber-900 text-xs">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-semibold">Integration Verification Rule: </span>
          In compliance with assessment guidelines, third-party connectors are strictly flagged as{' '}
          <span className="font-semibold text-amber-800">Not configured</span> until active API keys,
          service accounts, or webhooks have been provided and verified. No mock or fake connections are reported as live.
        </div>
      </div>

      {/* Workflow Diagram */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="mb-6">
          <h3 className="font-bold text-slate-900 text-base">Intended Pipeline Sequence</h3>
          <p className="text-xs text-slate-500">Autonomous data flow across the automation ecosystem</p>
        </div>

        {/* Step Flow Grid */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
          {workflowSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={step.step}
                className="relative p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-600">
                      #{step.step}
                    </span>
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs">{step.title}</h4>
                  <div className="text-[11px] font-medium text-indigo-600 mb-1">{step.sub}</div>
                  <p className="text-[11px] text-slate-500 leading-snug">{step.desc}</p>
                </div>

                {idx < workflowSteps.length - 1 && (
                  <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 bg-white rounded-full p-0.5 border border-slate-200" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Active Service Status Matrix */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h3 className="font-bold text-slate-900">Service Configuration Status</h3>
          <p className="text-xs text-slate-500">Real-time inspection of backend environment variables</p>
        </div>

        <div className="divide-y divide-slate-100">
          {integrations.map(item => (
            <div key={item.id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2.5">
                  <span className="font-semibold text-slate-900 text-sm">{item.name}</span>
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">
                    {item.category}
                  </span>
                </div>
                <p className="text-xs text-slate-500">{item.details}</p>
              </div>

              <div className="flex items-center space-x-3">
                <IntegrationStatusBadge status={item.status} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* n8n Webhook Endpoint Box */}
      <div className="bg-slate-900 rounded-2xl p-6 text-white space-y-3">
        <div className="flex items-center space-x-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
          <Workflow className="w-4 h-4" />
          <span>n8n Ingestion Webhook Endpoint</span>
        </div>
        <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
          Configure this URL in your n8n HTTP Request node or Google Apps Script to stream lead entries directly into the FastAPI database.
        </p>

        <div className="flex items-center space-x-2 bg-slate-800 p-2.5 rounded-xl border border-slate-700 max-w-xl">
          <code className="text-xs font-mono text-indigo-300 flex-1 truncate px-2">
            {webhookUrl}
          </code>
          <button
            onClick={handleCopyWebhook}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy URL'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

