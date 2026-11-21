import React, { useState, useEffect } from 'react';
import type { Lead, PriorityLevel, EmailDeliveryStatus } from '../types';
import { fetchLeads, createLead } from '../services/api';
import { PriorityBadge, StatusBadge } from '../components/Badge';
import { LeadDetailsModal } from '../components/LeadDetailsModal';
import { NewLeadModal } from '../components/NewLeadModal';
import { EmptyState } from '../components/EmptyState';
import {
  Search,
  Filter,
  ArrowUpDown,
  Plus,
  RefreshCw,
  Building2
} from 'lucide-react';

interface LeadsPageProps {
  initialPriorityFilter?: PriorityLevel | 'All';
  pageTitle?: string;
}

export const LeadsPage: React.FC<LeadsPageProps> = ({
  initialPriorityFilter = 'All',
  pageTitle = 'Lead Management Table',
}) => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<PriorityLevel | 'All'>(initialPriorityFilter);
  const [statusFilter, setStatusFilter] = useState<EmailDeliveryStatus | 'All'>('All');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isNewLeadOpen, setIsNewLeadOpen] = useState(false);

  const loadLeads = async () => {
    setLoading(true);
    const res = await fetchLeads({
      priority: priorityFilter !== 'All' ? priorityFilter : undefined,
      email_status: statusFilter !== 'All' ? statusFilter : undefined,
      search: search.trim() || undefined,
    });
    setLeads(res.leads);
    setLoading(false);
  };

  useEffect(() => {
    loadLeads();
  }, [priorityFilter, statusFilter, search]);

  const handleCreateLead = async (leadData: Omit<Lead, 'id' | 'created_at' | 'processed_at'>) => {
    await createLead(leadData);
    await loadLeads();
  };

  // Sort leads client-side
  const sortedLeads = [...leads].sort((a, b) => {
    const timeA = new Date(a.created_at).getTime();
    const timeB = new Date(b.created_at).getTime();
    return sortOrder === 'desc' ? timeB - timeA : timeA - timeB;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">{pageTitle}</h2>
          <p className="text-sm text-slate-500 mt-1">
            Real-time qualified leads, contact credentials, requested services, and AI email drafts.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => loadLeads()}
            title="Refresh lead data"
            className="p-2 text-slate-500 hover:text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsNewLeadOpen(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Inbound Lead</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-4 justify-between items-center">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search name, company, email..."
            className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 text-slate-800"
          />
        </div>

        {/* Filters and Sorting */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Priority filter */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-600">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={priorityFilter}
              onChange={e => setPriorityFilter(e.target.value as PriorityLevel | 'All')}
              className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:outline-hidden focus:ring-1 focus:ring-indigo-500 font-medium text-slate-700"
            >
              <option value="All">All Priorities</option>
              <option value="High">High Priority</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Email Status filter */}
          <div className="flex items-center space-x-1.5 text-xs text-slate-600">
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value as EmailDeliveryStatus | 'All')}
              className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:outline-hidden focus:ring-1 focus:ring-indigo-500 font-medium text-slate-700"
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Sent">Sent</option>
              <option value="Failed">Failed</option>
            </select>
          </div>

          {/* Date sort order */}
          <button
            onClick={() => setSortOrder(prev => (prev === 'desc' ? 'asc' : 'desc'))}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" />
            <span>{sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
          </button>
        </div>
      </div>

      {/* Leads Content */}
      {sortedLeads.length === 0 ? (
        <EmptyState
          title="No matching leads found"
          description="Try modifying your search keywords or clearing active filters to view all leads."
          actionText="Clear Filters"
          onAction={() => {
            setSearch('');
            setPriorityFilter('All');
            setStatusFilter('All');
          }}
        />
      ) : (
        <>
          {/* Desktop & Tablet Table View */}
          <div className="hidden md:block bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    <th className="py-3 px-6">Lead Name</th>
                    <th className="py-3 px-6">Company</th>
                    <th className="py-3 px-6">Email</th>
                    <th className="py-3 px-6">Service Required</th>
                    <th className="py-3 px-6">Budget</th>
                    <th className="py-3 px-6">Priority</th>
                    <th className="py-3 px-6">Email Status</th>
                    <th className="py-3 px-6">Date Received</th>
                    <th className="py-3 px-6 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {sortedLeads.map(lead => (
                    <tr
                      key={lead.id}
                      onClick={() => setSelectedLead(lead)}
                      className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                    >
                      <td className="py-3.5 px-6 font-semibold text-slate-900">{lead.name}</td>
                      <td className="py-3.5 px-6 text-slate-700 font-medium">{lead.company}</td>
                      <td className="py-3.5 px-6 text-slate-500 text-xs">{lead.email}</td>
                      <td className="py-3.5 px-6 text-slate-700">{lead.service}</td>
                      <td className="py-3.5 px-6 font-semibold text-slate-900">{lead.budget}</td>
                      <td className="py-3.5 px-6">
                        <PriorityBadge priority={lead.priority} />
                      </td>
                      <td className="py-3.5 px-6">
                        <StatusBadge status={lead.email_status} />
                      </td>
                      <td className="py-3.5 px-6 text-xs text-slate-500">
                        {new Date(lead.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 px-6 text-right" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => setSelectedLead(lead)}
                          className="px-3 py-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile Friendly Card Layout */}
          <div className="grid grid-cols-1 gap-3 md:hidden">
            {sortedLeads.map(lead => (
              <div
                key={lead.id}
                onClick={() => setSelectedLead(lead)}
                className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3 cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900">{lead.name}</h4>
                    <div className="flex items-center space-x-1 text-xs text-slate-500">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" />
                      <span>{lead.company}</span>
                    </div>
                  </div>
                  <PriorityBadge priority={lead.priority} />
                </div>

                <div className="text-xs space-y-1 text-slate-600">
                  <div><span className="text-slate-400">Service:</span> {lead.service}</div>
                  <div><span className="text-slate-400">Budget:</span> <span className="font-semibold">{lead.budget}</span></div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                  <StatusBadge status={lead.email_status} />
                  <span className="text-slate-400">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

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
