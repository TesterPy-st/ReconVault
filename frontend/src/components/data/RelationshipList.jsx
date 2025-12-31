// ReconVault RelationshipList Component

import React from 'react';
import { motion } from 'framer-motion';
import Badge from '../ui/Badge';

const RelationshipList = ({ relationships = [], loading = false, onViewEntity }) => {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-cyber-darker rounded-lg p-4 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-cyber-light rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-cyber-light rounded w-1/3 mb-2" />
                <div className="h-3 bg-cyber-light rounded w-1/4" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  if (relationships.length === 0) {
    return (
      <div className="text-center py-8">
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
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
        <h3 className="text-lg font-bold text-neon-green mb-2">No relationships found</h3>
        <p className="text-cyber-gray text-sm">
          Relationships will appear as entities are discovered
        </p>
      </div>
    );
  }
  
  const relationshipTypes = {
    owns: { label: 'Owns', color: 'neon-green' },
    hosts: { label: 'Hosts', color: 'neon-blue' },
    resolves_to: { label: 'Resolves To', color: 'neon-purple' },
    associated_with: { label: 'Associated With', color: 'neon-pink' },
    located_at: { label: 'Located At', color: 'yellow' },
    part_of: { label: 'Part Of', color: 'green' },
    depends_on: { label: 'Depends On', color: 'blue' },
    communicates_with: { label: 'Communicates With', color: 'purple' },
    contains: { label: 'Contains', color: 'pink' },
    derived_from: { label: 'Derived From', color: 'cyan' },
  };
  
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-cyber-gray uppercase">
          Relationships ({relationships.length})
        </h3>
      </div>
      
      {relationships.map((relationship, index) => {
        const typeConfig = relationshipTypes[relationship.type] || {
          label: relationship.type,
          color: 'default',
        };
        
        return (
          <motion.div
            key={relationship.id || index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-cyber-darker rounded-lg p-4 hover:border-cyber-border/50 border border-transparent transition-all cursor-pointer group"
            onClick={() => onViewEntity?.(relationship.target || relationship)}
          >
            {/* Source entity */}
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-cyber-light flex items-center justify-center text-neon-green">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neon-green truncate">
                  {relationship.source_name || relationship.source?.name || 'Unknown'}
                </p>
                <p className="text-xs text-cyber-gray capitalize">
                  {relationship.source_type || relationship.source?.type?.replace('_', ' ')}
                </p>
              </div>
            </div>
            
            {/* Relationship type arrow */}
            <div className="flex items-center justify-center mb-3">
              <div className="flex items-center gap-2 px-3 py-1 bg-cyber-light rounded-full">
                <Badge variant={typeConfig.color} size="small">
                  {typeConfig.label}
                </Badge>
              </div>
            </div>
            
            {/* Target entity */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-cyber-light flex items-center justify-center text-neon-blue">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neon-blue truncate">
                  {relationship.target_name || relationship.target?.name || 'Unknown'}
                </p>
                <p className="text-xs text-cyber-gray capitalize">
                  {relationship.target_type || relationship.target?.type?.replace('_', ' ')}
                </p>
              </div>
              
              {/* Confidence indicator */}
              {relationship.confidence !== undefined && (
                <div className="text-right">
                  <span className="text-xs text-cyber-gray">Confidence</span>
                  <p className="text-sm font-mono text-neon-purple">
                    {relationship.confidence}%
                  </p>
                </div>
              )}
            </div>
            
            {/* Hover action hint */}
            <div className="mt-3 pt-3 border-t border-cyber-border opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-xs text-cyber-gray flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Click to view details
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default RelationshipList;
