import React from 'react';
import type { Lead } from '../types';
import { Modal } from './Modal';
import { PriorityBadge, StatusBadge } from './Badge';
import { Mail, Phone, Building2, DollarSign, Calendar, Sparkles, Send } from 'lucide-react';

interface LeadDetailsModalProps {
  lead: Lead | null;
  isOpen: boolean;
  onClose: () => void;
}

export const LeadDetailsModal: React.FC<LeadDetailsModalProps> = ({ lead, isOpen, onClose }) => {
  if (!lead) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Lead Inspection & AI Qualification" maxWidth="max-w-3xl">
      <div className="space-y-6">
        {/* Header Summary */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div>
            <h4 className="text-xl font-bold text-slate-900">{lead.name}</h4>
            <div className="flex items-center space-x-2 text-sm text-slate-500 mt-1">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span>{lead.company}</span>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <PriorityBadge priority={lead.priority} />
            <StatusBadge status={lead.email_status} />
          </div>
        </div>

        {/* Contact & Deal Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Contact Information</div>
            
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Mail className="w-4 h-4 text-indigo-500 shrink-0" />
              <a href={`mailto:${lead.email}`} className="text-indigo-600 hover:underline">{lead.email}</a>
            </div>

            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Phone className="w-4 h-4 text-slate-400 shrink-0" />
              <span>{lead.phone || 'No phone provided'}</span>
            </div>

            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
              <span>Received: {new Date(lead.created_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Project & Commercials</div>
            
            <div className="text-sm">
              <span className="text-slate-500">Service Required:</span>{' '}
              <span className="font-semibold text-slate-900">{lead.service}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm">
              <DollarSign className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="text-slate-500">Budget Range:</span>{' '}
              <span className="font-semibold text-slate-900">{lead.budget}</span>
            </div>

            <div className="text-xs text-slate-500 pt-1">
              <span>Processed: </span>
              <span className="text-slate-700">
                {lead.processed_at ? new Date(lead.processed_at).toLocaleString() : 'Pending pipeline execution'}
              </span>
            </div>
          </div>
        </div>

        {/* Project Description */}
        <div className="p-4 rounded-xl border border-slate-200 bg-white">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Project Scope & Inbound Message</div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
            {lead.description || 'No additional project description submitted.'}
          </p>
        </div>

        {/* AI Qualification & Reasoning */}
        <div className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/50 space-y-2">
          <div className="flex items-center space-x-2 text-indigo-900 font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>Google Gemini AI Lead Scoring Analysis</span>
          </div>
          <p className="text-xs text-indigo-800 leading-relaxed">
            {lead.priority_reason || 'AI scoring prioritizes leads based on verified enterprise budget, clear project requirements, and prompt delivery expectations.'}
          </p>
        </div>

        {/* AI Generated Email Draft */}
        <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <Send className="w-3.5 h-3.5 text-slate-500" />
              <span>Automated Follow-Up Email Sequence</span>
            </div>
            <StatusBadge status={lead.email_status} />
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-sm space-y-2 font-mono">
            <div className="text-xs text-slate-500 font-sans pb-1 border-b border-slate-200">
              <span className="font-semibold">Subject:</span> {lead.email_subject || `Inquiry regarding ${lead.service}`}
            </div>
            <div className="text-slate-800 whitespace-pre-wrap text-xs font-sans leading-relaxed pt-1">
              {lead.email_body || 'Email content is currently being generated by the follow-up automation pipeline.'}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </Modal>
  );
};

