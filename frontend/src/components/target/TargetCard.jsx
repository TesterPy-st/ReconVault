// ReconVault TargetCard Component

import React from 'react';
import { motion } from 'framer-motion';
import Badge from '../ui/Badge';

const TargetCard = ({ target, onClick, onEdit, onDelete }) => {
  const statusConfig = {
    pending: { variant: 'pending', label: 'Pending' },
    queued: { variant: 'processing', label: 'Queued' },
    processing: { variant: 'processing', label: 'Processing' },
    completed: { variant: 'completed', label: 'Completed' },
    failed: { variant: 'failed', label: 'Failed' },
    cancelled: { variant: 'default', label: 'Cancelled' },
  };
  
  const typeIcons = {
    domain: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
      </svg>
    ),
    ip_address: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    email: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    phone: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
    social_media: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    person: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
    organization: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
  };
  
  const status = statusConfig[target.status] || { variant: 'default', label: target.status };
  
  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  return (
    <motion.div
      className="bg-cyber-light rounded-lg border border-cyber-border p-4 cursor-pointer hover:border-neon-green transition-all group"
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.99 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyber-darker flex items-center justify-center text-neon-green">
            {typeIcons[target.type] || typeIcons.domain}
          </div>
          <div>
            <h3 className="font-semibold text-neon-green truncate max-w-[200px]">
              {target.value}
            </h3>
            <p className="text-xs text-cyber-gray capitalize">
              {target.type?.replace('_', ' ')}
            </p>
          </div>
        </div>
        
        <Badge variant={status.variant} size="small">
          {status.label}
        </Badge>
      </div>
      
      {/* Details */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-cyber-gray">Entities Found</span>
          <span className="text-neon-blue font-mono">{target.entity_count || 0}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-cyber-gray">Risk Score</span>
          <Badge.Risk score={target.risk_score || 0} size="small" />
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-cyber-gray">Created</span>
          <span className="text-cyber-gray font-mono text-xs">
            {formatDate(target.created_at)}
          </span>
        </div>
      </div>
      
      {/* Progress bar for processing */}
      {target.status === 'processing' && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-cyber-gray mb-1">
            <span>Progress</span>
            <span>{target.progress || 0}%</span>
          </div>
          <div className="h-1.5 bg-cyber-darker rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-neon-green to-neon-blue"
              initial={{ width: 0 }}
              animate={{ width: `${target.progress || 0}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      )}
      
      {/* Actions */}
      <div className="flex items-center gap-2 pt-3 border-t border-cyber-border opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick?.(target);
          }}
          className="flex-1 px-3 py-1.5 bg-neon-green/20 text-neon-green text-sm rounded-lg hover:bg-neon-green/30 transition-colors"
        >
          View Details
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit?.(target);
          }}
          className="p-1.5 text-cyber-gray hover:text-neon-blue transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete?.(target);
          }}
          className="p-1.5 text-cyber-gray hover:text-neon-pink transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </motion.div>
  );
};

export default TargetCard;
