// ReconVault EntityPanel Component

import React from 'react';
import { motion } from 'framer-motion';
import Badge from '../ui/Badge';

const EntityPanel = ({ entity, onClose, onViewEntity }) => {
  if (!entity) return null;
  
  const getRiskBadge = (score) => {
    if (score >= 80) return { label: 'Critical', variant: 'critical' };
    if (score >= 60) return { label: 'High', variant: 'high' };
    if (score >= 40) return { label: 'Medium', variant: 'medium' };
    return { label: 'Low', variant: 'low' };
  };
  
  const riskBadge = getRiskBadge(entity.risk_score || 0);
  
  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      className="fixed right-0 top-16 bottom-0 w-96 bg-cyber-light border-l border-cyber-border z-30 overflow-y-auto"
    >
      {/* Header */}
      <div className="sticky top-0 bg-cyber-light border-b border-cyber-border p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-neon-green font-cyber">Entity Details</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4 space-y-6">
        {/* Entity header */}
        <div className="text-center">
          <div className="w-20 h-20 mx-auto rounded-full bg-cyber-darker flex items-center justify-center mb-4 border-2 border-neon-green/30">
            <span className="text-3xl font-bold text-neon-green font-cyber">
              {entity.name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
          <h3 className="text-xl font-bold text-neon-green">{entity.name}</h3>
          <p className="text-cyber-gray capitalize">{entity.type?.replace('_', ' ')}</p>
          <div className="mt-2">
            <Badge variant={riskBadge.variant} size="medium">
              {riskBadge.label} Risk
            </Badge>
          </div>
        </div>
        
        {/* Risk score visualization */}
        <div className="bg-cyber-darker rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-cyber-gray">Risk Score</span>
            <span className="text-lg font-bold text-neon-green">{entity.risk_score || 0}%</span>
          </div>
          <div className="h-3 bg-cyber-light rounded-full overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${
                entity.risk_score >= 80
                  ? 'bg-neon-pink'
                  : entity.risk_score >= 60
                  ? 'bg-orange-500'
                  : entity.risk_score >= 40
                  ? 'bg-yellow-500'
                  : 'bg-neon-green'
              }`}
              initial={{ width: 0 }}
              animate={{ width: `${entity.risk_score || 0}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          
          {/* Risk breakdown */}
          {entity.risk_factors && (
            <div className="mt-4 space-y-2">
              <p className="text-xs text-cyber-gray uppercase">Risk Factors</p>
              {entity.risk_factors.map((factor, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <div className="w-1.5 h-1.5 rounded-full bg-neon-pink" />
                  <span className="text-cyber-gray">{factor}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Details */}
        <div className="bg-cyber-darker rounded-lg p-4">
          <h4 className="text-sm font-semibold text-neon-green mb-3">Details</h4>
          <dl className="space-y-2 text-sm">
            {entity.value && (
              <div className="flex justify-between">
                <dt className="text-cyber-gray">Value</dt>
                <dd className="text-neon-green font-mono truncate max-w-[150px]">
                  {entity.value}
                </dd>
              </div>
            )}
            {entity.source && (
              <div className="flex justify-between">
                <dt className="text-cyber-gray">Source</dt>
                <dd className="text-neon-blue font-mono truncate max-w-[150px]">
                  {entity.source}
                </dd>
              </div>
            )}
            {entity.confidence !== undefined && (
              <div className="flex justify-between">
                <dt className="text-cyber-gray">Confidence</dt>
                <dd className="text-neon-purple font-mono">{entity.confidence}%</dd>
              </div>
            )}
            {entity.created_at && (
              <div className="flex justify-between">
                <dt className="text-cyber-gray">Discovered</dt>
                <dd className="text-cyber-gray">
                  {new Date(entity.created_at).toLocaleDateString()}
                </dd>
              </div>
            )}
          </dl>
        </div>
        
        {/* Tags */}
        {entity.tags && entity.tags.length > 0 && (
          <div className="bg-cyber-darker rounded-lg p-4">
            <h4 className="text-sm font-semibold text-neon-green mb-3">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {entity.tags.map((tag, index) => (
                <Badge key={index} variant="default" size="small">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onViewEntity?.(entity)}
            className="flex-1 px-4 py-2 bg-neon-green/20 text-neon-green rounded-lg hover:bg-neon-green/30 transition-colors text-sm font-medium"
          >
            View Full Details
          </button>
          <button className="px-4 py-2 bg-cyber-darker text-cyber-gray rounded-lg hover:text-neon-green transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default EntityPanel;
