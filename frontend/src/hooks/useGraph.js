// Custom hook for graph state management
import { useState, useEffect, useCallback, useRef } from 'react';
import graphService from '../services/graphService';
import webSocketService from '../services/websocket';
import { PERFORMANCE } from '../utils/constants';

export const useGraph = (initialFilters = {}) => {
  // Graph state
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [graphStats, setGraphStats] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Performance tracking
  const [performance, setPerformance] = useState({
    fps: 0,
    renderTime: 0,
    nodeCount: 0,
    edgeCount: 0
  });
  
  // Refs for performance optimization
  const animationFrameRef = useRef();
  const lastFrameTimeRef = useRef();
  const nodeCountRef = useRef(0);
  const edgeCountRef = useRef(0);
  
  // Load initial graph data
  const loadGraphData = useCallback(async (newFilters = filters) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await graphService.loadGraphData(newFilters);
      
      setNodes(data.nodes);
      setEdges(data.edges);
      setLastUpdate(data.lastUpdate || new Date());
      
      // Update performance metrics
      nodeCountRef.current = data.nodes.length;
      edgeCountRef.current = data.edges.length;
      
      console.log(`[useGraph] Loaded ${data.nodes.length} nodes and ${data.edges.length} edges`);
      
    } catch (err) {
      console.error('[useGraph] Error loading graph data:', err);
      setError(err.message || 'Failed to load graph data');
    } finally {
      setLoading(false);
    }
  }, [filters]);
  
  // Performance monitoring
  useEffect(() => {
    const measurePerformance = () => {
      const now = performance.now();
      const lastFrameTime = lastFrameTimeRef.current;
      
      if (lastFrameTime) {
        const deltaTime = now - lastFrameTime;
        const fps = 1000 / deltaTime;
        const renderTime = deltaTime;
        
        setPerformance(prev => ({
          ...prev,
          fps: Math.round(fps),
          renderTime: Math.round(renderTime),
          nodeCount: nodeCountRef.current,
          edgeCount: edgeCountRef.current
        }));
      }
      
      lastFrameTimeRef.current = now;
      animationFrameRef.current = requestAnimationFrame(measurePerformance);
    };
    
    animationFrameRef.current = requestAnimationFrame(measurePerformance);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);
  
  // Graph data event listeners
  useEffect(() => {
    const unsubscribeGraphDataLoaded = graphService.onGraphDataLoaded((data) => {
      setNodes(data.nodes);
      setEdges(data.edges);
      setLastUpdate(data.lastUpdate || new Date());
      nodeCountRef.current = data.nodes.length;
      edgeCountRef.current = data.edges.length;
    });
    
    const unsubscribeEntityCreated = graphService.onEntityCreated((entity) => {
      setNodes(prev => {
        const exists = prev.find(n => n.id === entity.id);
        if (exists) {
          return prev.map(n => n.id === entity.id ? entity : n);
        } else {
          nodeCountRef.current += 1;
          return [...prev, entity];
        }
      });
    });
    
    const unsubscribeEntityUpdated = graphService.onEntityUpdated((entity) => {
      setNodes(prev => prev.map(n => n.id === entity.id ? entity : n));
    });
    
    const unsubscribeEntityDeleted = ({ id }) => {
      setNodes(prev => {
        nodeCountRef.current = Math.max(0, nodeCountRef.current - 1);
        return prev.filter(n => n.id !== id);
      });
      setEdges(prev => {
        const removedEdges = prev.filter(e => e.source === id || e.target === id);
        edgeCountRef.current = Math.max(0, edgeCountRef.current - removedEdges.length);
        return prev.filter(e => e.source !== id && e.target !== id);
      });
      
      // Clear selection if deleted entity was selected
      if (selectedNode?.id === id) {
        setSelectedNode(null);
      }
    };
    
    const unsubscribeRelationshipCreated = graphService.onRelationshipCreated((relationship) => {
      setEdges(prev => {
        const exists = prev.find(e => e.id === relationship.id);
        if (exists) {
          return prev.map(e => e.id === relationship.id ? relationship : e);
        } else {
          edgeCountRef.current += 1;
          return [...prev, relationship];
        }
      });
    });
    
    const unsubscribeRelationshipDeleted = (relationship) => {
      setEdges(prev => {
        edgeCountRef.current = Math.max(0, edgeCountRef.current - 1);
        return prev.filter(e => e.id !== relationship.id);
      });
      
      // Clear selection if deleted relationship was selected
      if (selectedEdge?.id === relationship.id) {
        setSelectedEdge(null);
      }
    };
    
    const unsubscribeCacheCleared = graphService.onCacheCleared(() => {
      setNodes([]);
      setEdges([]);
      setSelectedNode(null);
      setSelectedEdge(null);
      setGraphStats(null);
      setLastUpdate(null);
      nodeCountRef.current = 0;
      edgeCountRef.current = 0;
    });
    
    // Subscribe to WebSocket events
    const unsubscribeWSConnected = webSocketService.onConnected(() => {
      console.log('[useGraph] WebSocket connected, reloading data');
      loadGraphData();
    });
    
    const unsubscribeWSEntityCreated = webSocketService.onEntityCreated((entity) => {
      graphService.onEntityCreated(entity); // Trigger service event
    });
    
    const unsubscribeWSEntityUpdated = webSocketService.onEntityUpdated((entity) => {
      graphService.onEntityUpdated(entity); // Trigger service event
    });
    
    const unsubscribeWSEntityDeleted = ({ id }) => {
      graphService.onEntityDeleted({ id }); // Trigger service event
    });
    
    const unsubscribeWSRelationshipCreated = webSocketService.onRelationshipCreated((relationship) => {
      graphService.onRelationshipCreated(relationship); // Trigger service event
    });
    
    const unsubscribeWSRelationshipDeleted = (relationship) => {
      graphService.onRelationshipDeleted(relationship); // Trigger service event
    });
    
    return () => {
      unsubscribeGraphDataLoaded();
      unsubscribeEntityCreated();
      unsubscribeEntityUpdated();
      unsubscribeEntityDeleted();
      unsubscribeRelationshipCreated();
      unsubscribeRelationshipDeleted();
      unsubscribeCacheCleared();
      unsubscribeWSConnected();
      unsubscribeWSEntityCreated();
      unsubscribeWSEntityUpdated();
      unsubscribeWSEntityDeleted();
      unsubscribeWSRelationshipCreated();
      unsubscribeWSRelationshipDeleted();
    };
  }, [loadGraphData, selectedNode, selectedEdge]);
  
  // Load data on mount
  useEffect(() => {
    loadGraphData();
  }, []);
  
  // Filter management
  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);
  
  const applyFilters = useCallback(() => {
    loadGraphData(filters);
  }, [filters, loadGraphData]);
  
  const clearFilters = useCallback(() => {
    const clearedFilters = {};
    setFilters(clearedFilters);
    loadGraphData(clearedFilters);
  }, [loadGraphData]);
  
  // Node selection
  const selectNode = useCallback((node) => {
    setSelectedNode(node);
    setSelectedEdge(null); // Clear edge selection
  }, []);
  
  const clearNodeSelection = useCallback(() => {
    setSelectedNode(null);
  }, []);
  
  // Edge selection
  const selectEdge = useCallback((edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null); // Clear node selection
  }, []);
  
  const clearEdgeSelection = useCallback(() => {
    setSelectedEdge(null);
  }, []);
  
  // Graph operations
  const refreshGraph = useCallback(() => {
    loadGraphData();
  }, [loadGraphData]);
  
  const exportGraph = useCallback(async (format = 'json') => {
    try {
      const data = await graphService.exportGraphData(format);
      return data;
    } catch (err) {
      console.error('[useGraph] Error exporting graph:', err);
      setError(err.message || 'Failed to export graph');
      throw err;
    }
  }, []);
  
  const clearGraph = useCallback(() => {
    graphService.clearCache();
  }, []);
  
  // Get filtered data
  const filteredData = useCallback(() => {
    if (!filters || Object.keys(filters).length === 0) {
      return { nodes, edges };
    }
    
    return graphService.filterGraphData(filters);
  }, [nodes, edges, filters]);
  
  // Get performance warnings
  const getPerformanceWarnings = useCallback(() => {
    const warnings = [];
    
    if (performance.nodeCount > PERFORMANCE.MAX_NODES * 0.8) {
      warnings.push(`High node count: ${performance.nodeCount} nodes`);
    }
    
    if (performance.edgeCount > PERFORMANCE.MAX_EDGES * 0.8) {
      warnings.push(`High edge count: ${performance.edgeCount} edges`);
    }
    
    if (performance.fps < PERFORMANCE.FPS_TARGET * 0.8) {
      warnings.push(`Low frame rate: ${performance.fps} FPS`);
    }
    
    if (performance.renderTime > 16) { // 60 FPS = 16.67ms per frame
      warnings.push(`Slow render time: ${performance.renderTime}ms`);
    }
    
    return warnings;
  }, [performance]);
  
  // Memoized values for performance
  const memoizedData = {
    nodes: nodes,
    edges: edges,
    selectedNode,
    selectedEdge,
    filters,
    loading,
    error,
    graphStats,
    lastUpdate,
    performance,
    filteredData: filteredData(),
    performanceWarnings: getPerformanceWarnings()
  };
  
  return {
    // Data
    ...memoizedData,
    
    // Actions
    loadGraphData,
    updateFilters,
    applyFilters,
    clearFilters,
    selectNode,
    clearNodeSelection,
    selectEdge,
    clearEdgeSelection,
    refreshGraph,
    exportGraph,
    clearGraph,
    
    // Computed values
    hasData: nodes.length > 0,
    hasSelection: selectedNode || selectedEdge,
    isPerformanceOptimized: performance.fps >= PERFORMANCE.FPS_TARGET
  };
};