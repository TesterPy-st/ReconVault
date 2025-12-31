// ReconVault IntelligencePanel Component

import React from 'react';
import { motion } from 'framer-motion';
import Badge from '../ui/Badge';

const IntelligencePanel = ({ intelligence = [], loading = false, onViewFinding }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-cyber-darker rounded-lg p-4 animate-pulse">
            <div className="h-4 bg-cyber-light rounded w-1/3 mb-2" />
            <div className="h-3 bg-cyber-light rounded w-2/3" />
          </div>
        ))}
      </div>
    );
  }
  
  if (intelligence.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="w-16 h-16 mx-auto text-cyber-gray mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        <h3 className="text-xl font-bold text-neon-green mb-2">No intelligence found</h3>
        <p className="text-cyber-gray">
          Intelligence findings will appear during reconnaissance
        </p>
      </div>
    );
  }
  
  const sourceConfig = {
    whois: { label: 'WHOIS', color: 'neon-green', icon: '🌐' },
    dns: { label: 'DNS', color: 'neon-blue', icon: '📡' },
    ssl: { label: 'SSL', color: 'neon-purple', icon: '🔒' },
    osint: { label: 'OSINT', color: 'neon-pink', icon: '🔍' },
    social: { label: 'Social', color: 'yellow', icon: '👥' },
    shodan: { label: 'Shodan', color: 'red', icon: '🏭' },
    censys: { label: 'Censys', color: 'blue', icon: '🔎' },
    google_dorking: { label: 'Google Dorking', color: 'green', icon: '🔎' },
  };
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-cyber-gray uppercase">
          Intelligence Findings ({intelligence.length})
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-cyber-gray">Filter by:</span>
          <select className="bg-cyber-darker border border-cyber-border rounded-lg px-2 py-1 text-xs text-neon-green focus:outline-none focus:border-neon-green">
            <option value="all">All Sources</option>
            {Object.entries(sourceConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>
      </div>
      
      {intelligence.map((item, index) => {
        const source = sourceConfig[item.source] || {
          label: item.source,
          color: 'default',
          icon: '📊',
        };
        
        return (
          <motion.div
            key={item.id || index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-cyber-darker rounded-lg border border-cyber-border p-4 hover:border-neon-green/30 transition-all cursor-pointer group"
            onClick={() => onViewFinding?.(item)}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">{source.icon}</span>
                <div>
                  <h4 className="text-sm font-medium text-neon-green">
                    {item.title || 'Intelligence Finding'}
                  </h4>
                  <p className="text-xs text-cyber-gray capitalize">
                    {source.label} • {item.category?.replace('_', ' ') || 'General'}
                  </p>
                </div>
              </div>
              <Badge variant={source.color} size="small">
                {source.label}
              </Badge>
            </div>
            
            {/* Content */}
            <p className="text-sm text-cyber-gray mb-3 line-clamp-2">
              {item.description || item.summary}
            </p>
            
            {/* Metadata */}
            <div className="flex items-center justify-between pt-3 border-t border-cyber-border">
              <div className="flex items-center gap-4">
                {item.confidence !== undefined && (
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-cyber-gray">Confidence:</span>
                    <span className="text-xs font-mono text-neon-blue">
                      {item.confidence}%
                    </span>
                  </div>
                )}
                {item.risk_score !== undefined && (
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-cyber-gray">Risk:</span>
                    <Badge.Risk score={item.risk_score} size="small" />
                  </div>
                )}
              </div>
              
              <span className="text-xs text-cyber-gray">
                {item.timestamp
                  ? new Date(item.timestamp).toLocaleDateString()
                  : ''}
              </span>
            </div>
            
            {/* Tags */}
            {item.tags && item.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {item.tags.slice(0, 5).map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-full bg-cyber-light text-xs text-cyber-gray"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
            
            {/* Hover action */}
            <div className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-xs text-neon-green flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                View full details
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default IntelligencePanel;
