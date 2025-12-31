// ReconVault TargetDetails Component

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import targetStore from '../../stores/targetStore';
import entityStore from '../../stores/entityStore';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import Loader from '../ui/Loader';
import RiskScore from '../data/RiskScore';

const TargetDetails = ({ target, onClose, onEdit }) => {
  const { selectedTarget, loading, fetchTarget, startRecon, stopRecon } = targetStore();
  const { fetchEntityRelationships, fetchEntityIntelligence, fetchEntityFindings } = entityStore();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [relatedData, setRelatedData] = useState({
    relationships: [],
    intelligence: [],
    findings: [],
  });
  
  const displayTarget = selectedTarget || target;
  
  useEffect(() => {
    if (displayTarget?.id) {
      fetchTarget(displayTarget.id);
      
      // Fetch related data
      Promise.all([
        fetchEntityRelationships(displayTarget.id),
        fetchEntityIntelligence(displayTarget.id),
        fetchEntityFindings(displayTarget.id),
      ]).then(([rels, intel, finds]) => {
        setRelatedData({
          relationships: rels?.data || [],
          intelligence: intel?.data || [],
          findings: finds?.data || [],
        });
      });
    }
  }, [displayTarget?.id]);
  
  const handleStartRecon = async () => {
    try {
      await startRecon(displayTarget.id);
    } catch (error) {
      console.error('Failed to start reconnaissance:', error);
    }
  };
  
  const handleStopRecon = async () => {
    try {
      await stopRecon(displayTarget.id);
    } catch (error) {
      console.error('Failed to stop reconnaissance:', error);
    }
  };
  
  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'entities', label: 'Entities' },
    { id: 'relationships', label: 'Relationships' },
    { id: 'intelligence', label: 'Intelligence' },
    { id: 'findings', label: 'Findings' },
  ];
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader size="large" text="Loading target details..." />
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-light transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <div>
            <h2 className="text-2xl font-bold text-neon-green font-cyber">
              {displayTarget?.value}
            </h2>
            <p className="text-cyber-gray capitalize">
              {displayTarget?.type?.replace('_', ' ')}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge.Status status={displayTarget?.status} size="medium" />
          <Button variant="ghost" size="small" onClick={() => onEdit?.(displayTarget)}>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </Button>
        </div>
      </div>
      
      {/* Actions */}
      <div className="flex items-center gap-3">
        {displayTarget?.status === 'processing' ? (
          <Button variant="danger" onClick={handleStopRecon}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
            Stop Recon
          </Button>
        ) : (
          <Button variant="primary" onClick={handleStartRecon}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Start Recon
          </Button>
        )}
        
        <Button variant="outline">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export
        </Button>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-cyber-border">
        <div className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-4 py-2 text-sm font-medium border-b-2 transition-colors
                ${
                  activeTab === tab.id
                    ? 'text-neon-green border-neon-green'
                    : 'text-cyber-gray border-transparent hover:text-neon-green'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab content */}
      <div className="min-h-[300px]">
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid gap-6 md:grid-cols-2"
          >
            {/* Info card */}
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6">
              <h3 className="text-lg font-semibold text-neon-green mb-4">Target Information</h3>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Type</dt>
                  <dd className="text-neon-green capitalize">{displayTarget?.type?.replace('_', ' ')}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Status</dt>
                  <dd><Badge.Status status={displayTarget?.status} size="small" /></dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Entities Found</dt>
                  <dd className="text-neon-blue font-mono">{displayTarget?.entity_count || 0}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Relationships</dt>
                  <dd className="text-neon-purple font-mono">{displayTarget?.relationship_count || 0}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Created</dt>
                  <dd className="text-cyber-gray text-sm">{formatDate(displayTarget?.created_at)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-cyber-gray">Updated</dt>
                  <dd className="text-cyber-gray text-sm">{formatDate(displayTarget?.updated_at)}</dd>
                </div>
              </dl>
            </div>
            
            {/* Risk assessment */}
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6">
              <h3 className="text-lg font-semibold text-neon-green mb-4">Risk Assessment</h3>
              <RiskScore score={displayTarget?.risk_score || 0} size="large" />
              
              {displayTarget?.source && (
                <div className="mt-4 pt-4 border-t border-cyber-border">
                  <dt className="text-sm text-cyber-gray mb-1">Source</dt>
                  <dd className="text-neon-blue text-sm truncate">{displayTarget.source}</dd>
                </div>
              )}
              
              {displayTarget?.description && (
                <div className="mt-4 pt-4 border-t border-cyber-border">
                  <dt className="text-sm text-cyber-gray mb-1">Description</dt>
                  <dd className="text-cyber-gray text-sm">{displayTarget.description}</dd>
                </div>
              )}
            </div>
          </motion.div>
        )}
        
        {activeTab === 'entities' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="text-xl font-bold text-neon-green mb-2">No entities found</h3>
            <p className="text-cyber-gray">Start reconnaissance to discover entities</p>
          </motion.div>
        )}
        
        {activeTab === 'relationships' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 className="text-xl font-bold text-neon-green mb-2">No relationships found</h3>
            <p className="text-cyber-gray">Relationships will appear as entities are discovered</p>
          </motion.div>
        )}
        
        {activeTab === 'intelligence' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-xl font-bold text-neon-green mb-2">No intelligence findings</h3>
            <p className="text-cyber-gray">Intelligence will be gathered during reconnaissance</p>
          </motion.div>
        )}
        
        {activeTab === 'findings' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-xl font-bold text-neon-green mb-2">No findings yet</h3>
            <p className="text-cyber-gray">Vulnerabilities and findings will appear here</p>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default TargetDetails;
