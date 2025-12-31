// ReconVault GraphCanvas Component

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import { motion } from 'framer-motion';
import graphStore from '../../stores/graphStore';
import uiStore from '../../stores/uiStore';
import NodeTooltip from './NodeTooltip';

const GraphCanvas = ({ data, onNodeClick, onLinkClick, height = 600 }) => {
  const fgRef = useRef(null);
  const containerRef = useRef(null);
  
  const {
    nodes,
    links,
    selectedNode,
    highlightedNode,
    view,
    setView,
    setSelectedNode,
    setHighlightedNode,
    fetchGraphData,
    filterNodes,
  } = graphStore();
  
  const { settings } = uiStore();
  
  const [tooltip, setTooltip] = useState(null);
  const [dimensions, setDimensions] = useState({ width: 800, height });
  
  // Handle resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: height,
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [height]);
  
  // Initial data load
  useEffect(() => {
    if (!data) {
      fetchGraphData();
    }
  }, [data, fetchGraphData]);
  
  // Get node color based on risk level
  const getNodeColor = useCallback((node) => {
    const score = node.risk_score || 0;
    if (score >= 80) return '#ff006e'; // Critical - neon pink
    if (score >= 60) return '#ff6600'; // High - orange
    if (score >= 40) return '#ffcc00'; // Medium - yellow
    return '#00ff88'; // Low - neon green
  }, []);
  
  // Get node size
  const getNodeSize = useCallback((node) => {
    const baseSize = 8;
    const score = node.risk_score || 0;
    const connections = node.connections || 1;
    return baseSize + (score / 15) + Math.log(connections) * 2;
  }, []);
  
  // Get link color
  const getLinkColor = useCallback((link) => {
    if (link.strength >= 0.8) return 'rgba(0, 255, 136, 0.6)'; // Strong - green
    if (link.strength >= 0.5) return 'rgba(0, 212, 255, 0.5)'; // Medium - blue
    return 'rgba(136, 136, 136, 0.4)'; // Weak - gray
  }, []);
  
  // Node canvas render
  const renderNode = useCallback((node, ctx, globalScale) => {
    const size = getNodeSize(node);
    const color = getNodeColor(node);
    const isSelected = selectedNode?.id === node.id;
    const isHighlighted = highlightedNode?.id === node.id || isSelected;
    
    // Glow effect
    if (isSelected) {
      ctx.shadowBlur = 20;
      ctx.shadowColor = color;
    } else if (isHighlighted) {
      ctx.shadowBlur = 10;
      ctx.shadowColor = color;
    }
    
    // Draw node
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
    
    // Border for selected/highlighted
    if (isSelected || isHighlighted) {
      ctx.lineWidth = 3;
      ctx.strokeStyle = isSelected ? '#ffffff' : color;
      ctx.stroke();
    }
    
    // Reset shadow
    ctx.shadowBlur = 0;
    
    // Draw label if zoomed in enough
    if (globalScale > 1.5 && settings.showLabels && node.name) {
      const fontSize = Math.max(10 / globalScale, 4);
      ctx.font = `${fontSize}px Share Tech Mono`;
      ctx.fillStyle = '#e0e0e0';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(node.name, node.x, node.y + size + 4);
    }
  }, [selectedNode, highlightedNode, settings.showLabels, getNodeSize, getNodeColor]);
  
  // Handle node click
  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    onNodeClick?.(node);
    
    // Center view on node
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(2, 2000);
    }
  }, [setSelectedNode, onNodeClick]);
  
  // Handle background click (deselect)
  const handleBgClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);
  
  // Handle zoom/pan
  const handleZoom = useCallback((transform) => {
    setView({ zoom: transform.k });
  }, [setView]);
  
  // Handle tooltip
  const handleNodeHover = useCallback((node) => {
    if (node) {
      setTooltip({
        x: node.x,
        y: node.y,
        node,
      });
      setHighlightedNode(node);
    } else {
      setTooltip(null);
      setHighlightedNode(null);
    }
  }, [setHighlightedNode]);
  
  // Graph configuration
  const graphConfig = {
    nodeLabel: 'name',
    nodeRelSize: 6,
    linkLabel: 'type',
    linkDirectionalParticles: 2,
    linkDirectionalParticleSpeed: 0.005,
    linkDirectionalParticleWidth: 2,
    backgroundColor: '#0a0e27',
    onEngineStop: () => {
      if (fgRef.current) {
        fgRef.current.zoomToFit(400);
      }
    },
  };
  
  return (
    <div ref={containerRef} className="relative bg-cyber-darker rounded-lg overflow-hidden border border-cyber-border">
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={{ nodes, links }}
        nodeColor={getNodeColor}
        nodeSize={getNodeSize}
        linkColor={getLinkColor}
        linkWidth={2}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        renderNode={renderNode}
        onNodeClick={handleNodeClick}
        onBackgroundClick={handleBgClick}
        onZoom={handleZoom}
        onNodeHover={handleNodeHover}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        {...graphConfig}
      />
      
      {/* Tooltip */}
      {tooltip && (
        <NodeTooltip
          x={tooltip.x}
          y={tooltip.y}
          node={tooltip.node}
          graphRef={fgRef}
        />
      )}
      
      {/* Empty state */}
      {nodes.length === 0 && !graphStore.getState().loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <div className="text-center">
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
            <h3 className="text-xl font-bold text-neon-green mb-2">No graph data</h3>
            <p className="text-cyber-gray">Add targets to generate the intelligence graph</p>
          </div>
        </motion.div>
      )}
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-cyber-light/90 backdrop-blur-sm rounded-lg p-3 border border-cyber-border">
        <h4 className="text-xs font-semibold text-cyber-gray uppercase mb-2">Legend</h4>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00ff88]" />
            <span className="text-xs text-cyber-gray">Low Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ffcc00]" />
            <span className="text-xs text-cyber-gray">Medium Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff6600]" />
            <span className="text-xs text-cyber-gray">High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#ff006e]" />
            <span className="text-xs text-cyber-gray">Critical Risk</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphCanvas;
