import React, { useState, useEffect } from 'react';
import type { EmailRecord, EmailDeliveryStatus } from '../types';
import { fetchEmails } from '../services/api';
import { StatusBadge, PriorityBadge } from '../components/Badge';
import { EmailPreviewModal } from '../components/EmailPreviewModal';
import { EmptyState } from '../components/EmptyState';
import { Search, RefreshCw } from 'lucide-react';

export const EmailHistoryPage: React.FC = () => {
  const [emails, setEmails] = useState<EmailRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<EmailDeliveryStatus | 'All'>('All');
  const [search, setSearch] = useState('');
  const [selectedEmail, setSelectedEmail] = useState<EmailRecord | null>(null);

  const loadEmails = async () => {
    setLoading(true);
    const data = await fetchEmails();
    setEmails(data);
    setLoading(false);
  };

  useEffect(() => {
    loadEmails();
  }, []);

  const filteredEmails = emails.filter(email => {
    const matchesStatus = statusFilter === 'All' || email.status === statusFilter;
    const query = search.toLowerCase();
    const matchesSearch =
      email.recipient.toLowerCase().includes(query) ||
      email.subject.toLowerCase().includes(query) ||
      email.lead_name.toLowerCase().includes(query) ||
      email.company.toLowerCase().includes(query);
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Automated Email History</h2>
          <p className="text-sm text-slate-500 mt-1">
            Log of AI-generated outreach messages, dispatch records, and delivery confirmation statuses.
          </p>
        </div>

        <button
          onClick={loadEmails}
          className="inline-flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors shadow-2xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh History</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row gap-4 justify-between items-center">
        {/* Status Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1 bg-slate-100 p-1 rounded-xl w-full sm:w-auto">
          {(['All', 'Sent', 'Draft', 'Pending', 'Failed', 'Delivery Unknown'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                statusFilter === tab
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search email, recipient, subject..."
            className="w-full pl-9 pr-4 py-2 text-sm rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 text-slate-800"
          />
        </div>
      </div>

      {/* Content Table */}
      {filteredEmails.length === 0 ? (
        <EmptyState
          title="No email records match criteria"
          description="Adjust your search filters or status selection to view past email communications."
          actionText="Show All Emails"
          onAction={() => {
            setStatusFilter('All');
            setSearch('');
          }}
        />
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-6">Recipient & Lead</th>
                  <th className="py-3 px-6">Subject Line</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Priority</th>
                  <th className="py-3 px-6">Timestamp</th>
                  <th className="py-3 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {filteredEmails.map(email => (
                  <tr
                    key={email.id}
                    onClick={() => setSelectedEmail(email)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                  >
                    <td className="py-3.5 px-6 font-medium text-slate-900">
                      <div>{email.recipient}</div>
                      <div className="text-xs text-slate-400 font-normal">
                        {email.lead_name} • {email.company}
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-slate-700 max-w-xs truncate font-medium">
                      {email.subject}
                    </td>
                    <td className="py-3.5 px-6">
                      <StatusBadge status={email.status} />
                    </td>
                    <td className="py-3.5 px-6">
                      <PriorityBadge priority={email.priority} />
                    </td>
                    <td className="py-3.5 px-6 text-xs text-slate-500">
                      {new Date(email.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-6 text-right" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={() => setSelectedEmail(email)}
                        className="px-3 py-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 rounded-lg transition-colors"
                      >
                        Preview
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Email Preview Modal */}
      <EmailPreviewModal
        email={selectedEmail}
        isOpen={!!selectedEmail}
        onClose={() => setSelectedEmail(null)}
      />
    </div>
  );
};
