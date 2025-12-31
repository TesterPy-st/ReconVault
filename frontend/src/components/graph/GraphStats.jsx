// ReconVault GraphStats Component

import React from 'react';
import { motion } from 'framer-motion';
import graphStore from '../../stores/graphStore';

const GraphStats = () => {
  const { stats, nodes, links } = graphStore();
  
  const statItems = [
    {
      label: 'Nodes',
      value: nodes.length || stats.nodeCount || 0,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      color: 'text-neon-green',
    },
    {
      label: 'Links',
      value: links.length || stats.linkCount || 0,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
      color: 'text-neon-blue',
    },
    {
      label: 'Avg Degree',
      value: (stats.avgDegree || 0).toFixed(1),
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      color: 'text-neon-purple',
    },
    {
      label: 'Density',
      value: `${((stats.density || 0) * 100).toFixed(1)}%`,
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
        </svg>
      ),
      color: 'text-neon-pink',
    },
  ];
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-cyber-light rounded-lg border border-cyber-border p-4"
    >
      <h3 className="text-sm font-semibold text-cyber-gray uppercase mb-4">
        Graph Statistics
      </h3>
      
      <div className="grid grid-cols-2 gap-4">
        {statItems.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-cyber-darker rounded-lg p-3"
          >
            <div className={`flex items-center gap-2 mb-1 ${item.color}`}>
              {item.icon}
              <span className="text-xs font-medium">{item.label}</span>
            </div>
            <p className="text-xl font-bold text-neon-green font-mono">
              {item.value}
            </p>
          </motion.div>
        ))}
      </div>
      
      {/* Central nodes */}
      {stats.centralNodes && stats.centralNodes.length > 0 && (
        <div className="mt-4 pt-4 border-t border-cyber-border">
          <h4 className="text-xs font-semibold text-cyber-gray uppercase mb-3">
            Central Nodes
          </h4>
          <div className="space-y-2">
            {stats.centralNodes.slice(0, 5).map((node, index) => (
              <div
                key={node.id}
                className="flex items-center justify-between bg-cyber-darker rounded-lg px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 flex items-center justify-center bg-cyber-light rounded text-xs text-neon-green font-bold">
                    {index + 1}
                  </span>
                  <span className="text-sm text-neon-green truncate max-w-[120px]">
                    {node.name}
                  </span>
                </div>
                <span className="text-xs text-cyber-gray font-mono">
                  {node.connections} links
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Communities */}
      {stats.communities && stats.communities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-cyber-border">
          <h4 className="text-xs font-semibold text-cyber-gray uppercase mb-3">
            Communities
          </h4>
          <div className="flex flex-wrap gap-2">
            {stats.communities.map((community) => (
              <div
                key={community.id}
                className="bg-cyber-darker rounded-lg px-3 py-1.5"
              >
                <span className="text-sm text-neon-blue">{community.name}</span>
                <span className="text-xs text-cyber-gray ml-2">
                  ({community.size})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default GraphStats;
