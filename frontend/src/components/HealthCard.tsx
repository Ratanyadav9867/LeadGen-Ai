import React from 'react';
import { CheckCircle2, AlertCircle, RefreshCw, Server, Database, Clock, Radio } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HealthCardProps {
  health: HealthStatus | null;
  loading: boolean;
  onRefresh: () => void;
}

export const HealthCard: React.FC<HealthCardProps> = ({ health, loading, onRefresh }) => {
  const isHealthy = health?.status === 'healthy';
  const isDown = health?.status === 'down';

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-lg ${isHealthy ? 'bg-emerald-50 text-emerald-600' : isDown ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600'}`}>
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Backend Health Endpoint</h3>
            <p className="text-xs text-slate-500">FastAPI & SQLite Integration Status</p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Check Now</span>
        </button>
      </div>

      <div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Status */}
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center space-x-3">
          {isHealthy ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0" />
          )}
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Service Status</div>
            <div className="text-sm font-semibold text-slate-900 capitalize">
              {health?.status || 'Unknown'}
            </div>
          </div>
        </div>

        {/* Database */}
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center space-x-3">
          <Database className="w-5 h-5 text-indigo-500 shrink-0" />
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Database (SQLite)</div>
            <div className="text-sm font-semibold text-slate-900 capitalize">
              {health?.database || 'Not verified'}
            </div>
          </div>
        </div>

        {/* Latency */}
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center space-x-3">
          <Clock className="w-5 h-5 text-amber-500 shrink-0" />
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Round-Trip Latency</div>
            <div className="text-sm font-semibold text-slate-900">
              {health?.latencyMs !== undefined ? `${health.latencyMs} ms` : '--'}
            </div>
          </div>
        </div>

        {/* Environment */}
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center space-x-3">
          <Radio className="w-5 h-5 text-sky-500 shrink-0" />
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Environment</div>
            <div className="text-sm font-semibold text-slate-900 capitalize">
              {health ? `${health.environment} (v${health.version})` : '--'}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Endpoint: <code className="text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">GET /api/health</code></span>
        <span>Last checked: {health?.timestamp || 'Never'}</span>
      </div>
    </div>
  );
};
