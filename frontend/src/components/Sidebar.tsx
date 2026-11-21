import React from 'react';
import { LayoutDashboard, Users, Zap, Mail, FileSpreadsheet, Settings } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: true },
    { icon: Users, label: 'Leads & Prospects', active: false, badge: 'Phase 2' },
    { icon: Zap, label: 'Gemini AI Scoring', active: false, badge: 'Phase 2' },
    { icon: Mail, label: 'Automated Follow-ups', active: false, badge: 'Phase 3' },
    { icon: FileSpreadsheet, label: 'Forms & Sheets Sync', active: false, badge: 'Phase 3' },
    { icon: Settings, label: 'Settings', active: false },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 min-h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="px-3 py-3 mb-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          CRM Navigation
        </div>
        <nav className="space-y-1">
          {menuItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  item.active
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white cursor-not-allowed opacity-75'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-normal">
                    {item.badge}
                  </span>
                )}
              </div>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-800/80 rounded-xl border border-slate-700/60 text-xs text-slate-400">
        <p className="font-medium text-slate-200 mb-1">Internship Assessment</p>
        <p>AI Automation Lead CRM</p>
        <p className="mt-2 text-[10px] text-slate-500">v0.1.0 • Monorepo Foundation</p>
      </div>
    </aside>
  );
};

