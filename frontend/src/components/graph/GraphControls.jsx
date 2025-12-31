// ReconVault GraphControls Component

import React from 'react';
import { motion } from 'framer-motion';
import graphStore from '../../stores/graphStore';

const GraphControls = () => {
  const {
    view,
    setView,
    setLayout,
    layout,
    fetchGraphData,
    filterNodes,
    saveSnapshot,
  } = graphStore();
  
  const handleZoomIn = () => {
    setView({ zoom: Math.min(view.zoom * 1.5, 5) });
  };
  
  const handleZoomOut = () => {
    setView({ zoom: Math.max(view.zoom / 1.5, 0.5) });
  };
  
  const handleResetView = () => {
    setView({ zoom: 1, center: { x: 0, y: 0 } });
  };
  
  const handleFitView = () => {
    setView({ zoom: 0.8 });
  };
  
  const handleToggleLabels = () => {
    setView({ showLabels: !view.showLabels });
  };
  
  const handleToggleLinks = () => {
    setView({ showLinks: !view.showLinks });
  };
  
  const handleRefresh = () => {
    fetchGraphData();
  };
  
  const handleLayoutChange = (type) => {
    setLayout({ type });
  };
  
  const handleSaveSnapshot = async () => {
    const name = `Snapshot ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`;
    await saveSnapshot(name);
  };
  
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2">
      {/* Main controls */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-cyber-light/95 backdrop-blur-sm rounded-lg border border-cyber-border p-2"
      >
        {/* Zoom controls */}
        <div className="flex flex-col gap-1 mb-2">
          <button
            onClick={handleZoomIn}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
            title="Zoom In"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          
          <button
            onClick={handleZoomOut}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
            title="Zoom Out"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>
          
          <button
            onClick={handleResetView}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
            title="Reset View"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
          
          <button
            onClick={handleFitView}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
            title="Fit to View"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
        </div>
        
        {/* Divider */}
        <div className="h-px bg-cyber-border my-2" />
        
        {/* Toggle controls */}
        <div className="flex flex-col gap-1">
          <button
            onClick={handleToggleLabels}
            className={`p-2 rounded-lg transition-colors ${
              view.showLabels
                ? 'text-neon-green bg-cyber-darker'
                : 'text-cyber-gray hover:text-neon-green hover:bg-cyber-darker'
            }`}
            title="Toggle Labels"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </button>
          
          <button
            onClick={handleToggleLinks}
            className={`p-2 rounded-lg transition-colors ${
              view.showLinks
                ? 'text-neon-green bg-cyber-darker'
                : 'text-cyber-gray hover:text-neon-green hover:bg-cyber-darker'
            }`}
            title="Toggle Links"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </button>
          
          <button
            onClick={handleRefresh}
            className="p-2 rounded-lg text-cyber-gray hover:text-neon-green hover:bg-cyber-darker transition-colors"
            title="Refresh"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        {/* Divider */}
        <div className="h-px bg-cyber-border my-2" />
        
        {/* Snapshot */}
        <button
          onClick={handleSaveSnapshot}
          className="w-full p-2 rounded-lg text-cyber-gray hover:text-neon-blue hover:bg-cyber-darker transition-colors"
          title="Save Snapshot"
        >
          <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </motion.div>
      
      {/* Zoom indicator */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="bg-cyber-light/95 backdrop-blur-sm rounded-lg border border-cyber-border px-3 py-2 text-center"
      >
        <span className="text-xs text-cyber-gray">Zoom</span>
        <p className="text-sm font-bold text-neon-green">
          {Math.round(view.zoom * 100)}%
        </p>
      </motion.div>
    </div>
  );
};

export default GraphControls;
