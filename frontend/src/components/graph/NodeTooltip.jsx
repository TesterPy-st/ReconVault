// ReconVault NodeTooltip Component

import React from 'react';
import { motion } from 'framer-motion';
import Badge from '../ui/Badge';

const NodeTooltip = ({ x, y, node, graphRef }) => {
  if (!node) return null;
  
  // Convert graph coordinates to screen coordinates
  const getScreenCoords = () => {
    if (!graphRef?.current || !node.x || !node.y) {
      return { left: '50%', top: '50%' };
    }
    
    // Use the graph instance's camera transform
    const graph = graphRef.current;
    if (graph.graph2d) {
      const canvas = graph.graph2d.canvas;
      const ctx = graph.graph2d.ctx;
      const transform = graph.graph2d.transform;
      
      const screenX = transform.applyX(node.x);
      const screenY = transform.applyY(node.y);
      
      return {
        left: `${Math.max(10, Math.min(canvas.width - 310, screenX))}px`,
        top: `${Math.max(10, Math.min(canvas.height - 150, screenY + 20))}px`,
      };
    }
    
    return { left: '50%', top: '50%' };
  };
  
  const coords = getScreenCoords();
  
  const getRiskBadge = (score) => {
    if (score >= 80) return { label: 'Critical', variant: 'critical' };
    if (score >= 60) return { label: 'High', variant: 'high' };
    if (score >= 40) return { label: 'Medium', variant: 'medium' };
    return { label: 'Low', variant: 'low' };
  };
  
  const riskBadge = getRiskBadge(node.risk_score || 0);
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed z-50 pointer-events-none"
      style={{
        left: coords.left,
        top: coords.top,
      }}
    >
      <div className="bg-cyber-light/95 backdrop-blur-sm rounded-lg border border-cyber-border p-4 shadow-xl min-w-[280px] max-w-[320px]">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-bold text-neon-green font-cyber text-sm">
              {node.name || node.id}
            </h3>
            <p className="text-xs text-cyber-gray capitalize">
              {node.type?.replace('_', ' ')}
            </p>
          </div>
          <Badge variant={riskBadge.variant} size="small">
            {riskBadge.label}
          </Badge>
        </div>
        
        {/* Details */}
        <div className="space-y-2 text-xs">
          {node.value && (
            <div className="flex justify-between">
              <span className="text-cyber-gray">Value</span>
              <span className="text-neon-green font-mono truncate max-w-[150px]">
                {node.value}
              </span>
            </div>
          )}
          
          {node.risk_score !== undefined && (
            <div className="flex justify-between">
              <span className="text-cyber-gray">Risk Score</span>
              <span className="text-neon-green font-mono">{node.risk_score}%</span>
            </div>
          )}
          
          {node.connections !== undefined && (
            <div className="flex justify-between">
              <span className="text-cyber-gray">Connections</span>
              <span className="text-neon-blue font-mono">{node.connections}</span>
            </div>
          )}
          
          {node.confidence !== undefined && (
            <div className="flex justify-between">
              <span className="text-cyber-gray">Confidence</span>
              <span className="text-neon-purple font-mono">{node.confidence}%</span>
            </div>
          )}
        </div>
        
        {/* Progress bar for risk */}
        <div className="mt-3 pt-3 border-t border-cyber-border">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-cyber-gray">Risk Level</span>
            <span className="text-neon-green">{node.risk_score || 0}%</span>
          </div>
          <div className="h-1.5 bg-cyber-darker rounded-full overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${
                node.risk_score >= 80
                  ? 'bg-neon-pink'
                  : node.risk_score >= 60
                  ? 'bg-orange-500'
                  : node.risk_score >= 40
                  ? 'bg-yellow-500'
                  : 'bg-neon-green'
              }`}
              initial={{ width: 0 }}
              animate={{ width: `${node.risk_score || 0}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
        
        {/* Arrow indicator */}
        <div
          className="absolute w-0 h-0 border-l-8 border-r-8 border-b-8 border-transparent border-b-cyber-border"
          style={{
            top: -8,
            left: 20,
          }}
        />
        <div
          className="absolute w-0 h-0 border-l-6 border-r-6 border-b-6 border-transparent border-b-cyber-light/95"
          style={{
            top: -5,
            left: 22,
          }}
        />
      </div>
    </motion.div>
  );
};

export default NodeTooltip;
