import React from 'react';
import { Menu, User } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HeaderProps {
  onMenuToggle: () => void;
  health: HealthStatus | null;
  onRefreshHealth: () => void;
  isDemoData?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  health,
  onRefreshHealth,
  isDemoData = false,
}) => {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      <div className="flex items-center space-x-3">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          aria-label="Toggle navigation drawer"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:block">
          <h2 className="text-sm font-semibold text-slate-800">Autonomous CRM Dashboard</h2>
          <p className="text-xs text-slate-400">Lead Scoring & Automated Outreach</p>
        </div>
      </div>

      <div className="flex items-center space-x-3 sm:space-x-4">
        {/* Demo Data Notice Indicator */}
        {isDemoData && (
          <div
            title="Demonstration dataset loaded for UI review. Add live leads via 'Add Inbound Lead' or backend API."
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-xs font-medium"
          >
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span className="hidden md:inline">Demo Dataset Active</span>
            <span className="md:hidden">Demo</span>
          </div>
        )}

        {/* Backend Health Status Pill */}
        <button
          onClick={onRefreshHealth}
          title="Click to re-check backend health"
          className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs transition-colors cursor-pointer"
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isHealthy ? 'bg-emerald-500' : 'bg-rose-500'
            }`}
          />
          <span className="text-slate-700 font-medium">
            {isHealthy ? 'Backend Connected' : 'Backend Degraded'}
          </span>
          {health?.latencyMs !== undefined && (
            <span className="text-slate-400 text-[10px] hidden sm:inline">
              ({health.latencyMs}ms)
            </span>
          )}
        </button>

        {/* User Pill */}
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700">
            <User className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold text-slate-700 hidden sm:inline">Operator</span>
        </div>
      </div>
    </header>
  );
};
