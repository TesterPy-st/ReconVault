// ReconVault Intelligence Page

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import IntelligencePanel from '../components/data/IntelligencePanel';
import RelationshipList from '../components/data/RelationshipList';
import Loader from '../components/ui/Loader';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import entityStore from '../stores/entityStore';

const IntelligencePage = () => {
  const {
    entities,
    intelligence,
    findings,
    loading,
    pagination,
    filters,
    stats,
    fetchEntities,
    fetchStats,
    searchEntities,
    setFilters,
  } = entityStore();
  
  const [activeTab, setActiveTab] = useState('intelligence');
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  
  useEffect(() => {
    fetchEntities();
    fetchStats();
  }, [fetchEntities, fetchStats]);
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchEntities(searchQuery);
    } else {
      fetchEntities();
    }
  };
  
  const handleTypeFilterChange = (type) => {
    setTypeFilter(type);
    setFilters({ type: type || null });
  };
  
  const handleRiskFilterChange = (level) => {
    setRiskFilter(level);
    setFilters({ riskLevel: level || null });
  };
  
  const tabs = [
    { id: 'intelligence', label: 'Intelligence', count: intelligence.length },
    { id: 'entities', label: 'Entities', count: pagination.total },
    { id: 'findings', label: 'Findings', count: findings.length },
  ];
  
  const statCards = [
    {
      label: 'Total Intelligence',
      value: intelligence.length,
      icon: '🧠',
      color: 'text-neon-green',
    },
    {
      label: 'Total Entities',
      value: pagination.total,
      icon: '📊',
      color: 'text-neon-blue',
    },
    {
      label: 'Findings',
      value: findings.length,
      icon: '🔍',
      color: 'text-neon-purple',
    },
    {
      label: 'High Risk',
      value: stats.byRiskLevel?.high || 0,
      icon: '⚠️',
      color: 'text-neon-pink',
    },
  ];
  
  return (
    <Layout>
      <MainContent>
        {/* Page header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-neon-green font-cyber">
              Intelligence
            </h1>
            <p className="text-cyber-gray">
              View gathered intelligence and discovered entities
            </p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-cyber-light rounded-lg border border-cyber-border p-4"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{stat.icon}</span>
                <div>
                  <p className="text-2xl font-bold text-neon-green font-mono">
                    {loading ? <Loader size="small" /> : stat.value}
                  </p>
                  <p className="text-sm text-cyber-gray">{stat.label}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Search and filters */}
        <div className="bg-cyber-light rounded-lg border border-cyber-border p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search intelligence..."
                  className="w-full bg-cyber-darker border border-cyber-border rounded-lg pl-10 pr-4 py-2.5 text-neon-green placeholder-cyber-gray/50 focus:outline-none focus:border-neon-green"
                />
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-cyber-gray"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </form>
            
            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              <select
                value={typeFilter}
                onChange={(e) => handleTypeFilterChange(e.target.value)}
                className="bg-cyber-darker border border-cyber-border rounded-lg px-4 py-2.5 text-neon-green focus:outline-none focus:border-neon-green"
              >
                <option value="">All Types</option>
                <option value="domain">Domain</option>
                <option value="ip_address">IP Address</option>
                <option value="email">Email</option>
                <option value="phone">Phone</option>
                <option value="person">Person</option>
                <option value="organization">Organization</option>
              </select>
              
              <select
                value={riskFilter}
                onChange={(e) => handleRiskFilterChange(e.target.value)}
                className="bg-cyber-darker border border-cyber-border rounded-lg px-4 py-2.5 text-neon-green focus:outline-none focus:border-neon-green"
              >
                <option value="">All Risk Levels</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
                <option value="critical">Critical Risk</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="border-b border-cyber-border mb-6">
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
                <span className="ml-2 px-2 py-0.5 rounded-full bg-cyber-darker text-xs">
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>
        
        {/* Content */}
        {loading ? (
          <div className="py-12">
            <Loader size="large" text="Loading intelligence..." />
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Main content */}
            <div className="lg:col-span-2">
              {activeTab === 'intelligence' && (
                <IntelligencePanel
                  intelligence={intelligence}
                  loading={loading}
                />
              )}
              
              {activeTab === 'entities' && (
                <div className="space-y-4">
                  {entities.length > 0 ? (
                    entities.map((entity) => (
                      <motion.div
                        key={entity.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-cyber-light rounded-lg border border-cyber-border p-4 hover:border-neon-green/30 transition-colors cursor-pointer"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-cyber-darker flex items-center justify-center text-neon-green font-bold text-lg">
                              {entity.name?.charAt(0)?.toUpperCase() || '?'}
                            </div>
                            <div>
                              <h3 className="font-semibold text-neon-green">{entity.name}</h3>
                              <p className="text-sm text-cyber-gray capitalize">
                                {entity.type?.replace('_', ' ')}
                              </p>
                            </div>
                          </div>
                          <Badge.Risk score={entity.risk_score || 0} />
                        </div>
                        
                        {entity.value && (
                          <p className="mt-3 text-sm text-cyber-gray font-mono">
                            {entity.value}
                          </p>
                        )}
                        
                        <div className="mt-3 pt-3 border-t border-cyber-border flex items-center justify-between">
                          <div className="flex items-center gap-4 text-xs text-cyber-gray">
                            <span>{entity.connections || 0} connections</span>
                            <span>Confidence: {entity.confidence || 0}%</span>
                          </div>
                          <Badge.Status status={entity.status || 'active'} size="small" />
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      <h3 className="text-xl font-bold text-neon-green mb-2">No entities found</h3>
                      <p className="text-cyber-gray">Start reconnaissance to discover entities</p>
                    </div>
                  )}
                </div>
              )}
              
              {activeTab === 'findings' && (
                <div className="text-center py-12">
                  <svg className="w-16 h-16 mx-auto text-cyber-gray mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="text-xl font-bold text-neon-green mb-2">No findings yet</h3>
                  <p className="text-cyber-gray">Vulnerabilities and findings will appear here</p>
                </div>
              )}
            </div>
            
            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick filters */}
              <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
                <h3 className="text-sm font-semibold text-neon-green mb-4">Quick Filters</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => handleRiskFilterChange('critical')}
                    className="w-full flex items-center justify-between p-3 bg-cyber-darker rounded-lg hover:bg-cyber-lighter transition-colors"
                  >
                    <span className="text-sm text-cyber-gray">Critical Risk</span>
                    <Badge variant="critical" size="small">
                      {stats.byRiskLevel?.critical || 0}
                    </Badge>
                  </button>
                  <button
                    onClick={() => handleRiskFilterChange('high')}
                    className="w-full flex items-center justify-between p-3 bg-cyber-darker rounded-lg hover:bg-cyber-lighter transition-colors"
                  >
                    <span className="text-sm text-cyber-gray">High Risk</span>
                    <Badge variant="high" size="small">
                      {stats.byRiskLevel?.high || 0}
                    </Badge>
                  </button>
                  <button
                    onClick={() => handleTypeFilterChange('domain')}
                    className="w-full flex items-center justify-between p-3 bg-cyber-darker rounded-lg hover:bg-cyber-lighter transition-colors"
                  >
                    <span className="text-sm text-cyber-gray">Domains</span>
                    <Badge variant="primary" size="small">
                      {stats.byType?.domain || 0}
                    </Badge>
                  </button>
                  <button
                    onClick={() => handleTypeFilterChange('ip_address')}
                    className="w-full flex items-center justify-between p-3 bg-cyber-darker rounded-lg hover:bg-cyber-lighter transition-colors"
                  >
                    <span className="text-sm text-cyber-gray">IP Addresses</span>
                    <Badge variant="secondary" size="small">
                      {stats.byType?.ip_address || 0}
                    </Badge>
                  </button>
                </div>
              </div>
              
              {/* Distribution */}
              <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
                <h3 className="text-sm font-semibold text-neon-green mb-4">Entity Distribution</h3>
                <div className="space-y-3">
                  {Object.entries(stats.byType || {}).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm text-cyber-gray capitalize">
                        {type.replace('_', ' ')}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-cyber-darker rounded-full overflow-hidden">
                          <div
                            className="h-full bg-neon-green rounded-full"
                            style={{
                              width: `${Math.min((count / pagination.total) * 100, 100)}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs text-cyber-gray w-8">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </MainContent>
    </Layout>
  );
};

export default IntelligencePage;
