// ReconVault Graph Page

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import GraphCanvas from '../components/graph/GraphCanvas';
import GraphControls from '../components/graph/GraphControls';
import GraphStats from '../components/graph/GraphStats';
import EntityPanel from '../components/data/EntityPanel';
import Loader from '../components/ui/Loader';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import graphStore from '../stores/graphStore';
import uiStore from '../stores/uiStore';

const GraphPage = () => {
  const {
    nodes,
    links,
    loading,
    selectedNode,
    searchQuery,
    searchResults,
    filters,
    stats,
    fetchGraphData,
    fetchStats,
    searchNodes,
    filterNodes,
    setSelectedNode,
    setSearchQuery,
    clearSearch,
  } = graphStore();
  
  const { settings } = uiStore();
  
  const [searchInput, setSearchInput] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [showStats, setShowStats] = useState(true);
  const [entityPanelOpen, setEntityPanelOpen] = useState(false);
  
  useEffect(() => {
    fetchGraphData();
    fetchStats();
  }, [fetchGraphData, fetchStats]);
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSearchQuery(searchInput);
      searchNodes(searchInput);
    }
  };
  
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    setEntityPanelOpen(true);
  };
  
  const handleClearSearch = () => {
    setSearchInput('');
    clearSearch();
  };
  
  const handleFilterChange = (key, value) => {
    filterNodes({ [key]: value });
  };
  
  const nodeTypeOptions = [
    { value: '', label: 'All Types' },
    { value: 'domain', label: 'Domain' },
    { value: 'ip_address', label: 'IP Address' },
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
    { value: 'person', label: 'Person' },
    { value: 'organization', label: 'Organization' },
    { value: 'network', label: 'Network' },
    { value: 'service', label: 'Service' },
  ];
  
  const riskLevelOptions = [
    { value: '', label: 'All Risk Levels' },
    { value: 'low', label: 'Low Risk' },
    { value: 'medium', label: 'Medium Risk' },
    { value: 'high', label: 'High Risk' },
    { value: 'critical', label: 'Critical Risk' },
  ];
  
  return (
    <Layout>
      <MainContent className="!p-0">
        <div className="flex h-[calc(100vh-64px)]">
          {/* Main graph area */}
          <div className="flex-1 relative">
            {/* Top bar */}
            <div className="absolute top-4 left-4 right-4 z-10 flex items-center gap-4">
              {/* Search */}
              <form onSubmit={handleSearch} className="flex-1 max-w-md">
                <div className="relative">
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Search nodes..."
                    className="w-full bg-cyber-light/95 backdrop-blur-sm border border-cyber-border rounded-lg pl-10 pr-10 py-2 text-neon-green placeholder-cyber-gray/50 focus:outline-none focus:border-neon-green"
                  />
                  <svg
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-cyber-gray"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  {searchInput && (
                    <button
                      type="button"
                      onClick={handleClearSearch}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-cyber-gray hover:text-neon-green"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </form>
              
              {/* Filter toggle */}
              <Button
                variant={showFilters ? 'primary' : 'outline'}
                size="small"
                onClick={() => setShowFilters(!showFilters)}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Filters
              </Button>
              
              {/* Stats toggle */}
              <Button
                variant={showStats ? 'primary' : 'outline'}
                size="small"
                onClick={() => setShowStats(!showStats)}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Stats
              </Button>
              
              {/* Refresh */}
              <Button
                variant="outline"
                size="small"
                onClick={() => fetchGraphData()}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </Button>
            </div>
            
            {/* Filters panel */}
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-16 left-4 z-10 bg-cyber-light/95 backdrop-blur-sm rounded-lg border border-cyber-border p-4 w-72"
              >
                <h3 className="text-sm font-semibold text-neon-green mb-4">Filters</h3>
                
                <div className="space-y-4">
                  <Select
                    label="Node Type"
                    value={filters.nodeTypes?.[0] || ''}
                    onChange={(value) => handleFilterChange('nodeTypes', value ? [value] : [])}
                    options={nodeTypeOptions}
                    searchable
                  />
                  
                  <Select
                    label="Risk Level"
                    value={filters.riskLevels?.[0] || ''}
                    onChange={(value) => handleFilterChange('riskLevels', value ? [value] : [])}
                    options={riskLevelOptions}
                  />
                  
                  <div className="flex items-center justify-between">
                    <label className="text-sm text-cyber-gray">Show Isolated</label>
                    <button
                      onClick={() => handleFilterChange('showIsolated', !filters.showIsolated)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        filters.showIsolated ? 'bg-neon-green' : 'bg-cyber-darker'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 rounded-full bg-white transition-transform ${
                          filters.showIsolated ? 'translate-x-6' : 'translate-x-0.5'
                        }`}
                      />
                    </button>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="small"
                    className="w-full"
                    onClick={() => {
                      setSearchInput('');
                      clearSearch();
                      fetchGraphData();
                    }}
                  >
                    Reset Filters
                  </Button>
                </div>
              </motion.div>
            )}
            
            {/* Graph canvas */}
            {loading && nodes.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <Loader size="large" text="Loading graph data..." />
              </div>
            ) : (
              <GraphCanvas
                onNodeClick={handleNodeClick}
                height={window.innerHeight - 80}
              />
            )}
            
            {/* Controls */}
            <GraphControls />
          </div>
          
          {/* Stats panel */}
          {showStats && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-80 border-l border-cyber-border bg-cyber-light overflow-y-auto hidden xl:block"
            >
              <div className="p-4">
                <GraphStats />
              </div>
            </motion.div>
          )}
          
          {/* Entity panel (right side) */}
          {entityPanelOpen && selectedNode && (
            <EntityPanel
              entity={selectedNode}
              onClose={() => {
                setEntityPanelOpen(false);
                setSelectedNode(null);
              }}
              onViewEntity={handleNodeClick}
            />
          )}
        </div>
      </MainContent>
    </Layout>
  );
};

export default GraphPage;
