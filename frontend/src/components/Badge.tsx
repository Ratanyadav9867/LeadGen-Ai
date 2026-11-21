import React from 'react';
import type { PriorityLevel, EmailDeliveryStatus, IntegrationStatus } from '../types';

export const PriorityBadge: React.FC<{ priority: PriorityLevel }> = ({ priority }) => {
  switch (priority) {
    case 'High':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-rose-500"></span>
          High Priority
        </span>
      );
    case 'Medium':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-amber-500"></span>
          Medium
        </span>
      );
    case 'Low':
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-slate-400"></span>
          Low
        </span>
      );
  }
};

export const StatusBadge: React.FC<{ status: EmailDeliveryStatus }> = ({ status }) => {
  switch (status) {
    case 'Sent':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-500"></span>
          Sent
        </span>
      );
    case 'Failed':
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-rose-500"></span>
          Failed
        </span>
      );
    case 'Pending':
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200/80">
          <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-amber-500"></span>
          Pending
        </span>
      );
  }
};

export const IntegrationStatusBadge: React.FC<{ status: IntegrationStatus }> = ({ status }) => {
  switch (status) {
    case 'Connected':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="w-2 h-2 mr-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Connected
        </span>
      );
    case 'Error':
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          <span className="w-2 h-2 mr-1.5 rounded-full bg-rose-500"></span>
          Error
        </span>
      );
    case 'Not configured':
    default:
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          <span className="w-2 h-2 mr-1.5 rounded-full bg-amber-400"></span>
          Not configured
        </span>
      );
  }
};

