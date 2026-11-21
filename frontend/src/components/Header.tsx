import React from 'react';
import { Sparkles, Bell, User } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-xs">
      <div className="flex items-center space-x-3">
        <div className="bg-indigo-600 p-2 rounded-lg text-white">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">LeadGen AI</h1>
          <p className="text-xs text-slate-500">Autonomous CRM & Follow-Up System</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-medium border border-indigo-100">
          Phase 1: Foundation
        </div>
        <button 
          title="Notifications" 
          aria-label="Notifications" 
          className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors"
        >
          <Bell className="w-5 h-5" />
        </button>
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-700">
            <User className="w-4 h-4" />
          </div>
          <span className="text-sm font-medium text-slate-700">Admin</span>
        </div>
      </div>
    </header>
  );
};

