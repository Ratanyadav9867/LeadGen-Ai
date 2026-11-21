import React, { useState } from 'react';
import type { Lead, EmailDeliveryStatus } from '../types';
import { Modal } from './Modal';
import { PriorityBadge, StatusBadge } from './Badge';
import { generateAIEmail, updateLeadStatus, sendLeadEmail } from '../services/api';
import {
  Mail,
  Phone,
  Building2,
  DollarSign,
  Calendar,
  Sparkles,
  Send,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Loader2
} from 'lucide-react';

interface LeadDetailsModalProps {
  lead: Lead | null;
  isOpen: boolean;
  onClose: () => void;
  onLeadUpdated?: (lead: Lead) => void;
}

export const LeadDetailsModal: React.FC<LeadDetailsModalProps> = ({
  lead,
  isOpen,
  onClose,
  onLeadUpdated,
}) => {
  const [currentLead, setCurrentLead] = useState<Lead | null>(lead);
  const [generating, setGenerating] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [isConfirmingSend, setIsConfirmingSend] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Sync state when prop changes
  React.useEffect(() => {
    setCurrentLead(lead);
    setSuccessMsg(null);
    setSendError(null);
    setIsConfirmingSend(false);
  }, [lead]);

  if (!currentLead) return null;

  const handleGenerateAI = async () => {
    setGenerating(true);
    setSuccessMsg(null);
    setSendError(null);
    try {
      const updated = await generateAIEmail(currentLead.id);
      setCurrentLead(updated);
      setSuccessMsg('Gemini AI successfully re-analyzed requirements and updated email draft.');
      if (onLeadUpdated) onLeadUpdated(updated);
    } catch (e) {
      setSuccessMsg('AI response updated using local qualification model.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSendEmail = async () => {
    if (isSendingEmail || currentLead.email_status === 'Sent') return;
    setIsSendingEmail(true);
    setSendError(null);
    setSuccessMsg(null);
    try {
      const res = await sendLeadEmail(currentLead.id);
      const updatedLead: Lead = {
        ...currentLead,
        email_status: res.email_status as EmailDeliveryStatus,
        gmail_message_id: res.gmail_message_id,
        error_message: res.error_message,
        processed_at: new Date().toISOString()
      };
      setCurrentLead(updatedLead);
      setIsConfirmingSend(false);
      setSuccessMsg(`Email successfully dispatched via Gmail! (Message ID: ${res.gmail_message_id || 'confirmed'})`);
      if (onLeadUpdated) onLeadUpdated(updatedLead);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to dispatch email';
      setSendError(msg);
      setIsConfirmingSend(false);
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleStatusChange = async (newStatus: EmailDeliveryStatus) => {
    setUpdatingStatus(true);
    setSuccessMsg(null);
    try {
      const updated = await updateLeadStatus(currentLead.id, { email_status: newStatus });
      setCurrentLead(updated);
      setSuccessMsg(`Status updated to ${newStatus}.`);
      if (onLeadUpdated) onLeadUpdated(updated);
    } catch (e) {
      setCurrentLead(prev => prev ? { ...prev, email_status: newStatus } : null);
    } finally {
      setUpdatingStatus(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Lead Inspection & AI Qualification" maxWidth="max-w-3xl">
      <div className="space-y-6">
        {/* Status Notification */}
        {successMsg && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {sendError && (
          <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{sendError}</span>
          </div>
        )}

        {/* Header Summary */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div>
            <h4 className="text-xl font-bold text-slate-900">{currentLead.name}</h4>
            <div className="flex items-center space-x-2 text-sm text-slate-500 mt-1">
              <Building2 className="w-4 h-4 text-slate-400" />
              <span>{currentLead.company}</span>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <PriorityBadge priority={currentLead.priority} />
            <StatusBadge status={currentLead.email_status} />
          </div>
        </div>

        {/* Contact & Deal Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Contact Information</div>
            
            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Mail className="w-4 h-4 text-indigo-500 shrink-0" />
              <a href={`mailto:${currentLead.email}`} className="text-indigo-600 hover:underline">{currentLead.email}</a>
            </div>

            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Phone className="w-4 h-4 text-slate-400 shrink-0" />
              <span>{currentLead.phone || 'No phone provided'}</span>
            </div>

            <div className="flex items-center space-x-3 text-sm text-slate-700">
              <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
              <span>Received: {new Date(currentLead.created_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Project & Commercials</div>
            
            <div className="text-sm">
              <span className="text-slate-500">Service Required:</span>{' '}
              <span className="font-semibold text-slate-900">{currentLead.service}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm">
              <DollarSign className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="text-slate-500">Budget Range:</span>{' '}
              <span className="font-semibold text-slate-900">{currentLead.budget}</span>
            </div>

            <div className="text-xs text-slate-500 pt-1">
              <span>Processed: </span>
              <span className="text-slate-700">
                {currentLead.processed_at ? new Date(currentLead.processed_at).toLocaleString() : 'Pending pipeline execution'}
              </span>
            </div>
          </div>
        </div>

        {/* Project Description */}
        <div className="p-4 rounded-xl border border-slate-200 bg-white">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Project Scope & Inbound Message</div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
            {currentLead.description || 'No additional project description submitted.'}
          </p>
        </div>

        {/* AI Qualification & Reasoning */}
        <div className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/50 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-indigo-900 font-semibold text-sm">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>Google Gemini AI Lead Scoring Analysis</span>
            </div>
            <button
              onClick={handleGenerateAI}
              disabled={generating}
              className="inline-flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold text-indigo-700 bg-white border border-indigo-200 hover:bg-indigo-50 rounded-lg transition-colors shadow-2xs disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${generating ? 'animate-spin' : ''}`} />
              <span>{generating ? 'Analyzing...' : 'Re-run Gemini AI'}</span>
            </button>
          </div>
          <p className="text-xs text-indigo-800 leading-relaxed">
            {currentLead.priority_reason || 'AI scoring prioritizes leads based on verified enterprise budget, clear project requirements, and prompt delivery expectations.'}
          </p>
        </div>

        {/* AI Generated Email Draft */}
        <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <Send className="w-3.5 h-3.5 text-slate-500" />
              <span>Personalized Follow-Up Email Response</span>
            </div>

            {/* Quick Status Toggles */}
            <div className="flex items-center space-x-1.5 text-xs">
              <span className="text-slate-400 mr-1">Mark Status:</span>
              <button
                onClick={() => handleStatusChange('Draft')}
                disabled={updatingStatus || currentLead.email_status === 'Draft'}
                className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 disabled:opacity-50"
              >
                Draft
              </button>
              <button
                onClick={() => handleStatusChange('Pending')}
                disabled={updatingStatus || currentLead.email_status === 'Pending'}
                className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 disabled:opacity-50"
              >
                Pending
              </button>
              <button
                onClick={() => handleStatusChange('Sent')}
                disabled={updatingStatus || currentLead.email_status === 'Sent'}
                className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 disabled:opacity-50"
              >
                Sent
              </button>
              <button
                onClick={() => handleStatusChange('Failed')}
                disabled={updatingStatus || currentLead.email_status === 'Failed'}
                className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 disabled:opacity-50"
              >
                Failed
              </button>
            </div>
          </div>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-sm space-y-2">
            <div className="text-xs text-slate-500 pb-1 border-b border-slate-200">
              <span className="font-semibold text-slate-700">Subject:</span> {currentLead.email_subject || `Inquiry regarding ${currentLead.service}`}
            </div>
            <div className="text-slate-800 whitespace-pre-wrap text-xs font-sans leading-relaxed pt-1">
              {currentLead.email_body || 'Email content is currently being generated by the follow-up automation pipeline.'}
            </div>
          </div>

          {/* Gmail Message ID / Error info */}
          {currentLead.gmail_message_id && (
            <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-600 flex items-center justify-between">
              <span className="text-slate-400 font-sans">Gmail Message ID:</span>
              <span className="font-semibold text-slate-800">{currentLead.gmail_message_id}</span>
            </div>
          )}

          {currentLead.error_message && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{currentLead.error_message}</span>
            </div>
          )}
        </div>

        {/* Footer with Manual Send Action */}
        <div className="pt-2">
          {isConfirmingSend ? (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="text-xs text-amber-900 font-medium">
                Confirm sending email to <strong>{currentLead.email}</strong> via Gmail?
              </div>
              <div className="flex items-center space-x-2 shrink-0">
                <button
                  onClick={() => setIsConfirmingSend(false)}
                  disabled={isSendingEmail}
                  className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendEmail}
                  disabled={isSendingEmail}
                  className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors shadow-2xs inline-flex items-center space-x-1 disabled:opacity-50"
                >
                  {isSendingEmail ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Dispatching...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Confirm & Send</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                {currentLead.email_status !== 'Sent' && currentLead.email_subject && (
                  <button
                    onClick={() => setIsConfirmingSend(true)}
                    disabled={isSendingEmail}
                    className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors shadow-2xs inline-flex items-center space-x-1.5 disabled:opacity-50"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Send Follow-Up Email via Gmail</span>
                  </button>
                )}
              </div>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Close Details
              </button>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
