import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { HealthCard } from './components/HealthCard';
import { fetchHealth } from './services/api';
import type { HealthStatus } from './types';
import { Layers, ShieldCheck, Cpu } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadHealth = async () => {
    setLoading(true);
    const data = await fetchHealth();
    setHealth(data);
    setLoading(false);
  };

  useEffect(() => {
    loadHealth();
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 p-8 max-w-6xl w-full mx-auto space-y-6">
          {/* Welcome Banner */}
          <div className="bg-linear-to-r from-indigo-700 to-indigo-900 rounded-2xl p-6 text-white shadow-lg shadow-indigo-900/10">
            <h2 className="text-2xl font-bold tracking-tight">Phase 1: Environment & Project Foundation</h2>
            <p className="mt-2 text-indigo-100 text-sm max-w-2xl leading-relaxed">
              Monorepo established with React + Vite + TypeScript frontend, Tailwind CSS styling, 
              FastAPI backend, SQLite persistence, and structured modules ready for AI lead qualification & n8n automation.
            </p>
          </div>

          {/* Backend Connectivity Status */}
          <HealthCard
            health={health}
            loading={loading}
            onRefresh={loadHealth}
          />

          {/* Architecture Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg w-fit mb-3">
                <Layers className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-slate-900">Clean Monorepo</h4>
              <p className="text-xs text-slate-500 mt-1">
                Modular separation of frontend (React), backend (FastAPI), automation (n8n), and docs.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
              <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg w-fit mb-3">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-slate-900">Health Verification</h4>
              <p className="text-xs text-slate-500 mt-1">
                Live round-trip diagnostics validating API responsiveness, CORS configuration, and SQLite connectivity.
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
              <div className="p-2 bg-purple-50 text-purple-600 rounded-lg w-fit mb-3">
                <Cpu className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-slate-900">Ready for AI & Automation</h4>
              <p className="text-xs text-slate-500 mt-1">
                Foundation laid for Gemini scoring models, Google Sheets/Forms ingestion, and automated Gmail sequences.
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
