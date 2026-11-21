import React, { useState, useEffect } from 'react';
import type { IntegrationItem, HealthStatus } from '../types';
import { fetchIntegrations } from '../services/api';
import { IntegrationStatusBadge } from '../components/Badge';
import { HealthCard } from '../components/HealthCard';
import {
  Lock,
  Server,
  FileSpreadsheet,
  Workflow,
  Sparkles,
  Mail,
  RefreshCw,
  ShieldCheck
} from 'lucide-react';

interface SettingsPageProps {
  health: HealthStatus | null;
  loadingHealth: boolean;
  onRefreshHealth: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  health,
  loadingHealth,
  onRefreshHealth,
}) => {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadIntegrations = async () => {
    setLoading(true);
    const data = await fetchIntegrations();
    setIntegrations(data);
    setLoading(false);
  };

  useEffect(() => {
    loadIntegrations();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System & Integration Settings</h2>
        <p className="text-sm text-slate-500 mt-1">
          Configuration status for Google Workspace, Gemini AI, n8n webhook pipelines, and local database.
        </p>
      </div>

      {/* Security Protocol Banner */}
      <div className="p-4 bg-indigo-50/80 border border-indigo-200 rounded-2xl flex items-start space-x-3 text-indigo-900 text-xs">
        <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-semibold">Zero Client Secrets Rule: </span>
          In adherence to enterprise application security, secret keys (`GEMINI_API_KEY`, Google service account credentials, etc.)
          are stored exclusively on the backend server environment (`.env`) and are never exposed or transmitted to client browser bundles.
        </div>
      </div>

      {/* Backend Infrastructure Diagnostics */}
      <div>
        <h3 className="font-bold text-slate-900 text-base mb-3">Backend Server & Database Status</h3>
        <HealthCard
          health={health}
          loading={loadingHealth}
          onRefresh={onRefreshHealth}
        />
      </div>

      {/* Integration Configuration Status Matrix */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900">Integration Credentials Checklist</h3>
            <p className="text-xs text-slate-500">Service connection readiness for Phase 3 & 4</p>
          </div>
          <button
            onClick={loadIntegrations}
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors"
            title="Refresh status"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="divide-y divide-slate-100">
          {/* Google Sheets */}
          <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 mt-0.5">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 text-sm">Google Sheets Integration</h4>
                <p className="text-xs text-slate-500">
                  Target spreadsheet ID configured via <code>GOOGLE_SHEET_ID</code>
                </p>
                <div className="mt-2 text-[11px] text-slate-400">
                  Authentication: Google Service Account Key JSON
                </div>
              </div>
            </div>
            <IntegrationStatusBadge
              status={integrations.find(i => i.id === 'google-sheets')?.status || 'Not configured'}
            />
          </div>

          {/* Gemini API */}
          <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <div className="p-2.5 rounded-xl bg-purple-50 text-purple-600 mt-0.5">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 text-sm">Google Gemini AI Engine</h4>
                <p className="text-xs text-slate-500">
                  API Key configured via <code>GEMINI_API_KEY</code> on backend
                </p>
                <div className="mt-2 text-[11px] text-slate-400">
                  Model: Gemini 1.5 / 2.0 Flash • Tasks: Lead Scoring & Follow-up Synthesis
                </div>
              </div>
            </div>
            <IntegrationStatusBadge
              status={integrations.find(i => i.id === 'gemini-ai')?.status || 'Not configured'}
            />
          </div>

          {/* Gmail */}
          <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <div className="p-2.5 rounded-xl bg-rose-50 text-rose-600 mt-0.5">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 text-sm">Gmail Automated Outreach</h4>
                <p className="text-xs text-slate-500">
                  Sender address set via <code>GMAIL_SENDER_ADDRESS</code>
                </p>
                <div className="mt-2 text-[11px] text-slate-400">
                  Protocol: OAuth2 / App Password SMTP / Google API Client
                </div>
              </div>
            </div>
            <IntegrationStatusBadge
              status={integrations.find(i => i.id === 'gmail')?.status || 'Not configured'}
            />
          </div>

          {/* n8n */}
          <div className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start space-x-3">
              <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 mt-0.5">
                <Workflow className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 text-sm">n8n Orchestration Workflow</h4>
                <p className="text-xs text-slate-500">
                  Webhook URL target: <code>N8N_WEBHOOK_URL</code>
                </p>
                <div className="mt-2 text-[11px] text-slate-400">
                  Workflow: Trigger ➔ Data Mapping ➔ AI Call ➔ Outreach ➔ Log
                </div>
              </div>
            </div>
            <IntegrationStatusBadge
              status={integrations.find(i => i.id === 'n8n')?.status || 'Not configured'}
            />
          </div>
        </div>
      </div>

      {/* Environment & Architecture Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
            <Server className="w-4 h-4 text-indigo-600" />
            <span>Monorepo Architecture</span>
          </div>
          <div className="text-xs text-slate-500 space-y-1">
            <div><span className="font-medium text-slate-700">Frontend:</span> React 19 + Vite + TypeScript + Tailwind CSS</div>
            <div><span className="font-medium text-slate-700">Backend:</span> Python 3.11 + FastAPI + SQLAlchemy 2.0</div>
            <div><span className="font-medium text-slate-700">Database:</span> SQLite (local development instance)</div>
            <div><span className="font-medium text-slate-700">CORS Policy:</span> Configured for http://localhost:5173</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm">
            <Lock className="w-4 h-4 text-emerald-600" />
            <span>Configuration Protocol</span>
          </div>
          <div className="text-xs text-slate-500 space-y-1 leading-relaxed">
            <p>
              To configure live integrations for Phase 3 and Phase 4, copy <code>backend/.env.example</code> to <code>backend/.env</code> and provide the legitimate service credentials.
            </p>
            <p className="text-[11px] text-slate-400 pt-1">
              Never commit the populated <code>.env</code> file into Git repository tracking.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
