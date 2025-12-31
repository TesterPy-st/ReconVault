// ReconVault Dashboard Page

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import targetStore from '../stores/targetStore';
import graphStore from '../stores/graphStore';
import uiStore from '../stores/uiStore';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import TargetList from '../components/target/TargetList';
import TargetForm from '../components/target/TargetForm';
import TargetDetails from '../components/target/TargetDetails';
import GraphCanvas from '../components/graph/GraphCanvas';
import GraphStats from '../components/graph/GraphStats';
import Loader from '../components/ui/Loader';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';

const Dashboard = () => {
  const { targets, stats, loading, fetchTargets, fetchStats } = targetStore();
  const { nodes, fetchGraphData } = graphStore();
  const { showSuccess, showError } = uiStore();
  
  const [activeView, setActiveView] = useState('targets');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  
  useEffect(() => {
    fetchTargets();
    fetchStats();
    fetchGraphData();
  }, [fetchTargets, fetchStats, fetchGraphData]);
  
  const handleCreateTarget = (target) => {
    setSelectedTarget(null);
    setShowCreateModal(true);
  };
  
  const handleEditTarget = (target) => {
    setSelectedTarget(target);
    setShowCreateModal(true);
  };
  
  const handleViewTarget = (target) => {
    setSelectedTarget(target);
    setShowDetails(true);
  };
  
  const handleDeleteTarget = async (target) => {
    if (window.confirm(`Are you sure you want to delete ${target.value}?`)) {
      try {
        await targetStore.getState().deleteTarget(target.id);
        showSuccess('Target deleted successfully');
      } catch (error) {
        showError('Failed to delete target');
      }
    }
  };
  
  const statCards = [
    {
      label: 'Total Targets',
      value: stats.total || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      color: 'text-neon-green',
      bgColor: 'bg-neon-green/10',
    },
    {
      label: 'Processing',
      value: stats.processing || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
      color: 'text-neon-blue',
      bgColor: 'bg-neon-blue/10',
    },
    {
      label: 'Completed',
      value: stats.completed || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      label: 'Entities Found',
      value: targets.reduce((sum, t) => sum + (t.entity_count || 0), 0),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      color: 'text-neon-purple',
      bgColor: 'bg-neon-purple/10',
    },
  ];
  
  return (
    <Layout>
      <MainContent>
        {/* Page header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-neon-green font-cyber">
              Dashboard
            </h1>
            <p className="text-cyber-gray">
              Cyber reconnaissance intelligence overview
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="primary" onClick={handleCreateTarget}>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Target
            </Button>
          </div>
        </div>
        
        {/* Stats grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-cyber-light rounded-lg border border-cyber-border p-4"
            >
              <div className={`flex items-center gap-3 mb-2 ${stat.color}`}>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  {stat.icon}
                </div>
              </div>
              <p className="text-2xl font-bold text-neon-green font-mono">
                {loading ? <Loader size="small" /> : stat.value}
              </p>
              <p className="text-sm text-cyber-gray">{stat.label}</p>
            </motion.div>
          ))}
        </div>
        
        {/* View toggle */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center bg-cyber-light rounded-lg border border-cyber-border p-1">
            <button
              onClick={() => setActiveView('targets')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === 'targets'
                  ? 'bg-neon-green text-cyber-dark'
                  : 'text-cyber-gray hover:text-neon-green'
              }`}
            >
              Targets
            </button>
            <button
              onClick={() => setActiveView('graph')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === 'graph'
                  ? 'bg-neon-green text-cyber-dark'
                  : 'text-cyber-gray hover:text-neon-green'
              }`}
            >
              Graph
            </button>
            <button
              onClick={() => setActiveView('overview')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeView === 'overview'
                  ? 'bg-neon-green text-cyber-dark'
                  : 'text-cyber-gray hover:text-neon-green'
              }`}
            >
              Overview
            </button>
          </div>
        </div>
        
        {/* Content */}
        {activeView === 'targets' && (
          <TargetList
            onSelectTarget={handleViewTarget}
            onEditTarget={handleEditTarget}
            onDeleteTarget={handleDeleteTarget}
          />
        )}
        
        {activeView === 'graph' && (
          <div className="grid gap-6 lg:grid-cols-4">
            <div className="lg:col-span-3">
              <GraphCanvas height={600} />
            </div>
            <div>
              <GraphStats />
            </div>
          </div>
        )}
        
        {activeView === 'overview' && (
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Quick actions */}
            <div className="lg:col-span-2 bg-cyber-light rounded-lg border border-cyber-border p-6">
              <h2 className="text-lg font-bold text-neon-green mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={handleCreateTarget}
                  className="p-4 bg-cyber-darker rounded-lg border border-cyber-border hover:border-neon-green transition-colors text-left group"
                >
                  <div className="w-10 h-10 rounded-lg bg-neon-green/20 flex items-center justify-center mb-3 group-hover:bg-neon-green/30 transition-colors">
                    <svg className="w-5 h-5 text-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-neon-green">New Target</h3>
                  <p className="text-sm text-cyber-gray mt-1">Add a new reconnaissance target</p>
                </button>
                
                <Link
                  to="/graph"
                  className="p-4 bg-cyber-darker rounded-lg border border-cyber-border hover:border-neon-blue transition-colors text-left group"
                >
                  <div className="w-10 h-10 rounded-lg bg-neon-blue/20 flex items-center justify-center mb-3 group-hover:bg-neon-blue/30 transition-colors">
                    <svg className="w-5 h-5 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-neon-blue">Graph Explorer</h3>
                  <p className="text-sm text-cyber-gray mt-1">Visualize entity relationships</p>
                </Link>
                
                <Link
                  to="/intelligence"
                  className="p-4 bg-cyber-darker rounded-lg border border-cyber-border hover:border-neon-purple transition-colors text-left group"
                >
                  <div className="w-10 h-10 rounded-lg bg-neon-purple/20 flex items-center justify-center mb-3 group-hover:bg-neon-purple/30 transition-colors">
                    <svg className="w-5 h-5 text-neon-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-neon-purple">Intelligence</h3>
                  <p className="text-sm text-cyber-gray mt-1">View gathered intelligence</p>
                </Link>
                
                <Link
                  to="/settings"
                  className="p-4 bg-cyber-darker rounded-lg border border-cyber-border hover:border-cyber-gray transition-colors text-left group"
                >
                  <div className="w-10 h-10 rounded-lg bg-cyber-gray/20 flex items-center justify-center mb-3 group-hover:bg-cyber-gray/30 transition-colors">
                    <svg className="w-5 h-5 text-cyber-gray" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <h3 className="font-medium text-cyber-gray">Settings</h3>
                  <p className="text-sm text-cyber-gray mt-1">Configure application settings</p>
                </Link>
              </div>
            </div>
            
            {/* Recent activity */}
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6">
              <h2 className="text-lg font-bold text-neon-green mb-4">Recent Targets</h2>
              <div className="space-y-3">
                {targets.slice(0, 5).map((target) => (
                  <div
                    key={target.id}
                    className="flex items-center justify-between p-3 bg-cyber-darker rounded-lg cursor-pointer hover:bg-cyber-lighter transition-colors"
                    onClick={() => handleViewTarget(target)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-cyber-light flex items-center justify-center">
                        <span className="text-neon-green text-sm font-bold">
                          {target.value.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-neon-green truncate max-w-[120px]">
                          {target.value}
                        </p>
                        <p className="text-xs text-cyber-gray capitalize">
                          {target.type?.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <Badge.Status status={target.status} size="small" />
                  </div>
                ))}
              </div>
              
              {targets.length > 5 && (
                <button
                  onClick={() => setActiveView('targets')}
                  className="w-full mt-4 py-2 text-sm text-neon-green hover:text-neon-blue transition-colors"
                >
                  View all targets →
                </button>
              )}
            </div>
          </div>
        )}
        
        {/* Create/Edit Target Modal */}
        <TargetForm
          isOpen={showCreateModal}
          onClose={() => {
            setShowCreateModal(false);
            setSelectedTarget(null);
          }}
          target={selectedTarget}
        />
        
        {/* Target Details Modal */}
        {showDetails && selectedTarget && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-cyber-light rounded-xl border border-cyber-border max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <TargetDetails
                  target={selectedTarget}
                  onClose={() => {
                    setShowDetails(false);
                    setSelectedTarget(null);
                  }}
                  onEdit={handleEditTarget}
                />
              </div>
            </div>
          </div>
        )}
      </MainContent>
    </Layout>
  );
};

export default Dashboard;
