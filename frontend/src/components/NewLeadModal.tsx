import React, { useState } from 'react';
import type { Lead, PriorityLevel, EmailDeliveryStatus } from '../types';
import { Modal } from './Modal';
import { Plus } from 'lucide-react';

interface NewLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (leadData: Omit<Lead, 'id' | 'created_at' | 'processed_at'>) => Promise<void>;
}

export const NewLeadModal: React.FC<NewLeadModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [service, setService] = useState('AI Workflow Automation');
  const [budget, setBudget] = useState('$5,000 - $10,000');
  const [description, setDescription] = useState('');
  const [priorityOption, setPriorityOption] = useState<'Auto' | PriorityLevel>('Auto');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!name.trim() || !company.trim() || !email.trim()) {
      setError('Name, Company, and Email are required.');
      return;
    }

    setSubmitting(true);
    try {
      const isManual = priorityOption !== 'Auto';
      await onSubmit({
        name: name.trim(),
        company: company.trim(),
        email: email.trim(),
        phone: phone.trim() || null,
        service,
        budget,
        description: description.trim() || null,
        priority: isManual ? (priorityOption as PriorityLevel) : undefined as any,
        priority_source: isManual ? 'manual' : 'ai',
        priority_reason: isManual ? `Manually assigned as ${priorityOption} priority by administrator.` : undefined,
        email_status: 'Pending' as EmailDeliveryStatus,
        email_subject: null,
        email_body: null,
      });
      onClose();
      // Reset form
      setName('');
      setCompany('');
      setEmail('');
      setPhone('');
      setDescription('');
      setPriorityOption('Auto');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit lead.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Inbound Lead" maxWidth="max-w-xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Lead Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="e.g. Rachel Adams"
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Company *</label>
            <input
              type="text"
              required
              value={company}
              onChange={e => setCompany(e.target.value)}
              placeholder="e.g. Nimbus Media"
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address *</label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="lead@company.com"
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Phone Number</label>
            <input
              type="tel"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              placeholder="+1 (555) 000-0000"
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Service Required</label>
            <select
              value={service}
              onChange={e => setService(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            >
              <option value="AI Workflow Automation">AI Workflow Automation</option>
              <option value="CRM Lead Scoring & Ingestion">CRM Lead Scoring & Ingestion</option>
              <option value="Automated Client Follow-Ups">Automated Client Follow-Ups</option>
              <option value="Google Workspace Integration">Google Workspace Integration</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Estimated Budget</label>
            <select
              value={budget}
              onChange={e => setBudget(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            >
              <option value="$3,000 - $5,000">$3,000 - $5,000</option>
              <option value="$5,000 - $10,000">$5,000 - $10,000</option>
              <option value="$10,000 - $25,000">$10,000 - $25,000</option>
              <option value="$25,000+">$25,000+</option>
            </select>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-xs font-semibold text-slate-700">Lead Priority (Optional Admin Override)</label>
            <span className="text-[11px] text-indigo-600 font-medium">Default: Auto (AI-Assigned)</span>
          </div>
          <select
            value={priorityOption}
            onChange={e => setPriorityOption(e.target.value as 'Auto' | PriorityLevel)}
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 bg-white"
          >
            <option value="Auto">Auto — Assign via Gemini AI Priority Engine (Recommended)</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
          <p className="text-[11px] text-slate-500 mt-1">
            Leave as Auto for automatic evaluation based on budget, urgency, and requirement.
          </p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Project Description / Scope</label>
          <textarea
            rows={3}
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Describe lead requirements, workflow goals, or special instructions..."
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="flex justify-end space-x-3 pt-3 border-t border-slate-200">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center space-x-1.5 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-xs transition-colors disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>{submitting ? 'Saving...' : 'Add Lead'}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

