import React from 'react';
import type { EmailRecord } from '../types';
import { Modal } from './Modal';
import { StatusBadge, PriorityBadge } from './Badge';
import { Mail, Clock, Building2 } from 'lucide-react';

interface EmailPreviewModalProps {
  email: EmailRecord | null;
  isOpen: boolean;
  onClose: () => void;
}

export const EmailPreviewModal: React.FC<EmailPreviewModalProps> = ({ email, isOpen, onClose }) => {
  if (!email) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Email Message Inspection" maxWidth="max-w-2xl">
      <div className="space-y-5">
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <div className="flex items-center space-x-2">
              <Mail className="w-4 h-4 text-indigo-600" />
              <span className="font-semibold text-sm text-slate-900">{email.subject}</span>
            </div>
            <StatusBadge status={email.status} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 pt-1">
            <div>
              <span className="text-slate-400">Recipient:</span>{' '}
              <span className="font-medium text-slate-800">{email.recipient}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              <span>{email.lead_name} ({email.company})</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{new Date(email.timestamp).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-slate-400">Lead Tier:</span>
              <PriorityBadge priority={email.priority} />
            </div>
            {email.gmail_message_id && (
              <div className="col-span-1 sm:col-span-2 pt-1 font-mono text-[11px] text-slate-500">
                <span className="text-slate-400 font-sans">Gmail Message ID:</span> {email.gmail_message_id}
              </div>
            )}
          </div>
        </div>

        {email.error_message && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
            <span className="font-semibold">Delivery Warning / Error:</span> {email.error_message}
          </div>
        )}

        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Email Body</div>
          <div className="p-4 bg-white border border-slate-200 rounded-xl text-sm text-slate-800 whitespace-pre-wrap leading-relaxed shadow-2xs font-sans">
            {email.body}
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

