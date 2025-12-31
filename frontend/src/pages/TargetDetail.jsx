// ReconVault TargetDetail Page

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import TargetDetails from '../components/target/TargetDetails';
import IntelligencePanel from '../components/data/IntelligencePanel';
import RelationshipList from '../components/data/RelationshipList';
import RiskScore from '../components/data/RiskScore';
import Loader from '../components/ui/Loader';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import targetStore from '../stores/targetStore';
import entityStore from '../stores/entityStore';

const TargetDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const { selectedTarget, loading, fetchTarget, startRecon, stopRecon, deleteTarget } = targetStore();
  const { selectedEntity, fetchEntity, relationships, intelligence } = entityStore();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  useEffect(() => {
    if (id) {
      fetchTarget(id);
    }
  }, [id, fetchTarget]);
  
  const handleStartRecon = async () => {
    try {
      await startRecon(id);
    } catch (error) {
      console.error('Failed to start reconnaissance:', error);
    }
  };
  
  const handleStopRecon = async () => {
    try {
      await stopRecon(id);
    } catch (error) {
      console.error('Failed to stop reconnaissance:', error);
    }
  };
  
  const handleDelete = async () => {
    try {
      await deleteTarget(id);
      navigate('/');
    } catch (error) {
      console.error('Failed to delete target:', error);
    }
  };
  
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'entities', label: 'Entities' },
    { id: 'relationships', label: 'Relationships' },
    { id: 'intelligence', label: 'Intelligence' },
    { id: 'findings', label: 'Findings' },
  ];
  
  if (loading && !selectedTarget) {
    return (
      <Layout>
        <MainContent>
          <div className="flex items-center justify-center h-[60vh]">
            <Loader size="large" text="Loading target details..." />
          </div>
        </MainContent>
      </Layout>
    );
  }
  
  if (!selectedTarget) {
    return (
      <Layout>
        <MainContent>
          <div className="text-center py-12">
            <h2 className="text-xl font-bold text-neon-green mb-2">Target not found</h2>
            <p className="text-cyber-gray mb-4">The target you're looking for doesn't exist.</p>
            <Button variant="primary" onClick={() => navigate('/')}>
              Back to Dashboard
            </Button>
          </div>
        </MainContent>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <MainContent>
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-light transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <div>
              <h1 className="text-2xl font-bold text-neon-green font-cyber">
                {selectedTarget.value}
              </h1>
              <p className="text-cyber-gray capitalize">
                {selectedTarget.type?.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge.Status status={selectedTarget.status} size="medium" />
            
            {selectedTarget.status === 'processing' ? (
              <Button variant="danger" size="small" onClick={handleStopRecon}>
                Stop Recon
              </Button>
            ) : (
              <Button variant="primary" size="small" onClick={handleStartRecon}>
                Start Recon
              </Button>
            )}
            
            <Button
              variant="ghost"
              size="small"
              onClick={() => setShowDeleteConfirm(true)}
              className="text-neon-pink hover:text-neon-pink"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </Button>
          </div>
        </div>
        
        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
            <p className="text-sm text-cyber-gray">Entities Found</p>
            <p className="text-2xl font-bold text-neon-green font-mono">
              {selectedTarget.entity_count || 0}
            </p>
          </div>
          <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
            <p className="text-sm text-cyber-gray">Relationships</p>
            <p className="text-2xl font-bold text-neon-blue font-mono">
              {selectedTarget.relationship_count || 0}
            </p>
          </div>
          <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
            <p className="text-sm text-cyber-gray">Intelligence</p>
            <p className="text-2xl font-bold text-neon-purple font-mono">
              {intelligence.length || 0}
            </p>
          </div>
          <div className="bg-cyber-light rounded-lg border border-cyber-border p-4 flex items-center justify-center">
            <RiskScore score={selectedTarget.risk_score || 0} size="small" showLabel={false} />
          </div>
        </div>
        
        {/* Progress bar for processing */}
        {selectedTarget.status === 'processing' && (
          <div className="mb-6 bg-cyber-light rounded-lg border border-cyber-border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-cyber-gray">Reconnaissance Progress</span>
              <span className="text-sm text-neon-green font-mono">
                {selectedTarget.progress || 0}%
              </span>
            </div>
            <div className="h-2 bg-cyber-darker rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-neon-green to-neon-blue"
                initial={{ width: 0 }}
                animate={{ width: `${selectedTarget.progress || 0}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}
        
        {/* Tabs */}
        <div className="border-b border-cyber-border mb-6">
          <div className="flex gap-4 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
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
        <div className="min-h-[400px]">
          {activeTab === 'overview' && (
            <TargetDetails
              target={selectedTarget}
              onClose={() => navigate('/')}
              onEdit={() => console.log('Edit target')}
            />
          )}
          
          {activeTab === 'entities' && (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="text-xl font-bold text-neon-green mb-2">No entities discovered</h3>
              <p className="text-cyber-gray">Start reconnaissance to discover entities</p>
            </div>
          )}
          
          {activeTab === 'relationships' && (
            <RelationshipList relationships={relationships} />
          )}
          
          {activeTab === 'intelligence' && (
            <IntelligencePanel intelligence={intelligence} />
          )}
          
          {activeTab === 'findings' && (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-bold text-neon-green mb-2">No findings yet</h3>
              <p className="text-cyber-gray">Vulnerabilities and findings will appear during reconnaissance</p>
            </div>
          )}
        </div>
        
        {/* Delete confirmation modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-cyber-light rounded-xl border border-cyber-border p-6 max-w-md w-full"
            >
              <h3 className="text-xl font-bold text-neon-green mb-2">Delete Target?</h3>
              <p className="text-cyber-gray mb-6">
                Are you sure you want to delete "{selectedTarget.value}"? This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <Button variant="ghost" onClick={() => setShowDeleteConfirm(false)}>
                  Cancel
                </Button>
                <Button variant="danger" onClick={handleDelete}>
                  Delete Target
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </MainContent>
    </Layout>
  );
};

export default TargetDetailPage;
