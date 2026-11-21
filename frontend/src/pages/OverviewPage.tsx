import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Lead, LeadStats, HealthStatus } from '../types';
import { fetchStats, fetchLeads, createLead } from '../services/api';
import { PriorityBadge, StatusBadge } from '../components/Badge';
import { LeadDetailsModal } from '../components/LeadDetailsModal';
import { NewLeadModal } from '../components/NewLeadModal';
import { HealthCard } from '../components/HealthCard';
import {
  Users,
  UserPlus,
  Flame,
  Send,
  AlertTriangle,
  ArrowRight,
  Plus,
  Info
} from 'lucide-react';

interface OverviewPageProps {
  health: HealthStatus | null;
  loadingHealth: boolean;
  onRefreshHealth: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  health,
  loadingHealth,
  onRefreshHealth,
}) => {
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [recentLeads, setRecentLeads] = useState<Lead[]>([]);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isNewLeadOpen, setIsNewLeadOpen] = useState(false);

  const loadData = async () => {
    setLoading(true);
    const [statsRes, leadsRes] = await Promise.all([
      fetchStats(),
      fetchLeads(),
    ]);
    setStats(statsRes.stats);
    setIsDemo(statsRes.isDemo || leadsRes.isDemo);
    setRecentLeads(leadsRes.leads.slice(0, 5));
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateLead = async (leadData: Omit<Lead, 'id' | 'created_at' | 'processed_at'>) => {
    await createLead(leadData);
    await loadData();
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Executive CRM Overview</h2>
          <p className="text-sm text-slate-500 mt-1">
            Autonomous pipeline metrics, lead scoring, and automated follow-up status.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsNewLeadOpen(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Inbound Lead</span>
          </button>
        </div>
      </div>

      {/* Explicit Demo Data Notice */}
      {isDemo && (
        <div className="flex items-start space-x-3 p-4 rounded-xl bg-amber-50/90 border border-amber-200 text-amber-900 text-xs">
          <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold">Demonstration Dataset Loaded: </span>
            The metrics and records shown below represent synthetic evaluation leads for demonstration and testing.
            Live customer submissions will populate automatically once Google Forms/Sheets webhooks are enabled.
          </div>
        </div>
      )}

      {/* 5 KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Leads */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Leads</span>
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">
              {loading ? '--' : stats?.total_leads}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">All ingested records</div>
          </div>
        </div>

        {/* New Leads */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">New Leads</span>
            <div className="p-2 rounded-lg bg-sky-50 text-sky-600">
              <UserPlus className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">
              {loading ? '--' : stats?.new_leads}
            </div>
            <div className="text-[11px] text-sky-600 font-medium mt-0.5">Awaiting follow-up</div>
          </div>
        </div>

        {/* Emails Sent / Contacted Leads */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Contacted Leads</span>
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Send className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-600">
              {loading ? '--' : stats?.emails_sent}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Automated outreach sent</div>
          </div>
        </div>

        {/* High Priority */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">High Priority Leads</span>
            <div className="p-2 rounded-lg bg-rose-50 text-rose-600">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-rose-600">
              {loading ? '--' : stats?.high_priority_leads}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Urgent & high-value</div>
          </div>
        </div>

        {/* Emails Failed */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Emails Failed</span>
            <div className="p-2 rounded-lg bg-rose-50 text-rose-600">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">
              {loading ? '--' : stats?.emails_failed}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Bounced / SMTP error</div>
          </div>
        </div>
      </div>

      {/* Backend Health Diagnostics (Preserving Phase 1) */}
      <HealthCard
        health={health}
        loading={loadingHealth}
        onRefresh={onRefreshHealth}
      />

      {/* Recent Leads Activity Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900">Recent Inbound Leads</h3>
            <p className="text-xs text-slate-500">Latest prospect submissions and their AI scoring status</p>
          </div>
          <Link
            to="/leads"
            className="inline-flex items-center space-x-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
          >
            <span>View All Leads</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-6">Lead</th>
                <th className="py-3 px-6">Company</th>
                <th className="py-3 px-6">Service</th>
                <th className="py-3 px-6">Budget</th>
                <th className="py-3 px-6">Priority</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {recentLeads.map(lead => (
                <tr key={lead.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-6 font-medium text-slate-900">
                    <div>{lead.name}</div>
                    <div className="text-xs text-slate-400 font-normal">{lead.email}</div>
                  </td>
                  <td className="py-3.5 px-6 text-slate-700">{lead.company}</td>
                  <td className="py-3.5 px-6 text-slate-700">{lead.service}</td>
                  <td className="py-3.5 px-6 text-slate-700 font-medium">{lead.budget}</td>
                  <td className="py-3.5 px-6">
                    <PriorityBadge priority={lead.priority} />
                  </td>
                  <td className="py-3.5 px-6">
                    <StatusBadge status={lead.email_status} />
                  </td>
                  <td className="py-3.5 px-6 text-right">
                    <button
                      onClick={() => setSelectedLead(lead)}
                      className="px-3 py-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Details Modal */}
      <LeadDetailsModal
        lead={selectedLead}
        isOpen={!!selectedLead}
        onClose={() => setSelectedLead(null)}
      />

      {/* New Lead Modal */}
      <NewLeadModal
        isOpen={isNewLeadOpen}
        onClose={() => setIsNewLeadOpen(false)}
        onSubmit={handleCreateLead}
      />
    </div>
  );
};
