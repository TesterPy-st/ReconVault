// ReconVault Graph Store - State Management with Zustand

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as graphService from '../services/graphService';
import { RISK_LEVELS } from '../utils/constants';

const initialState = {
  nodes: [],
  links: [],
  selectedNode: null,
  highlightedNode: null,
  loading: false,
  error: null,
  stats: {
    nodeCount: 0,
    linkCount: 0,
    avgDegree: 0,
    density: 0,
    centralNodes: [],
    communities: [],
  },
  filters: {
    nodeTypes: [],
    riskLevels: [],
    showIsolated: false,
    minConnections: 0,
    maxDepth: 2,
  },
  layout: {
    type: 'force',
    options: {
      forceStrength: -30,
      linkDistance: 100,
      nodeStrength: 30,
      collideStrength: 0.5,
    },
  },
  view: {
    zoom: 1,
    center: { x: 0, y: 0 },
    showLabels: true,
    showLinks: true,
  },
  searchQuery: '',
  searchResults: [],
  snapshots: [],
  currentSnapshot: null,
};

const graphStore = create(
  devtools(
    (set, get) => ({
      ...initialState,

      // Basic Actions
      setGraphData: (data) =>
        set({
          nodes: data.nodes || [],
          links: data.links || [],
        }),

      setNodes: (nodes) => set({ nodes }),
      
      setLinks: (links) => set({ links }),
      
      setSelectedNode: (node) => set({ selectedNode: node }),
      
      setHighlightedNode: (node) => set({ highlightedNode: node }),
      
      setLoading: (loading) => set({ loading }),
      
      setError: (error) => set({ error }),
      
      setStats: (stats) => set({ stats }),
      
      setFilters: (filters) =>
        set((state) => ({
          filters: { ...state.filters, ...filters },
        })),
      
      setLayout: (layout) =>
        set((state) => ({
          layout: { ...state.layout, ...layout },
        })),
      
      setLayoutOptions: (options) =>
        set((state) => ({
          layout: {
            ...state.layout,
            options: { ...state.layout.options, ...options },
          },
        })),
      
      setView: (view) =>
        set((state) => ({
          view: { ...state.view, ...view },
        })),
      
      setSearchQuery: (query) => set({ searchQuery: query }),
      
      setSearchResults: (results) => set({ searchResults: results }),
      
      setSnapshots: (snapshots) => set({ snapshots }),
      
      setCurrentSnapshot: (snapshot) => set({ currentSnapshot: snapshot }),

      // Async Actions
      fetchGraphData: async (params = {}) => {
        set({ loading: true, error: null });
        
        try {
          const data = await graphService.getGraphData(params);
          
          set({
            nodes: data.nodes || [],
            links: data.links || [],
            stats: data.stats || get().stats,
            loading: false,
          });
          
          return data;
        } catch (error) {
          console.error('Error fetching graph data:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch graph data',
            loading: false,
          });
          throw error;
        }
      },

      fetchTargetGraph: async (targetId, params = {}) => {
        set({ loading: true, error: null });
        
        try {
          const data = await graphService.getTargetGraphData(targetId, params);
          
          set({
            nodes: data.nodes || [],
            links: data.links || [],
            loading: false,
          });
          
          return data;
        } catch (error) {
          console.error('Error fetching target graph:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch target graph',
            loading: false,
          });
          throw error;
        }
      },

      fetchEntityGraph: async (entityId, depth = 2) => {
        set({ loading: true, error: null });
        
        try {
          const data = await graphService.getEntityGraphData(entityId, depth);
          
          set({
            nodes: data.nodes || [],
            links: data.links || [],
            loading: false,
          });
          
          return data;
        } catch (error) {
          console.error('Error fetching entity graph:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch entity graph',
            loading: false,
          });
          throw error;
        }
      },

      fetchStats: async () => {
        try {
          const stats = await graphService.getGraphStats();
          set({ stats });
          return stats;
        } catch (error) {
          console.error('Error fetching graph stats:', error);
        }
      },

      searchNodes: async (query) => {
        if (!query || query.length < 2) {
          set({ searchResults: [], searchQuery: query });
          return;
        }
        
        try {
          const results = await graphService.searchGraphNodes(query);
          set({ searchResults: results, searchQuery: query });
        } catch (error) {
          console.error('Error searching nodes:', error);
          set({ searchResults: [] });
        }
      },

      filterNodes: async (filters = {}) => {
        const currentFilters = get().filters;
        const mergedFilters = { ...currentFilters, ...filters };
        
        set({ loading: true, filters: mergedFilters });
        
        try {
          const data = await graphService.filterGraphNodes(mergedFilters);
          set({
            nodes: data.nodes || [],
            links: data.links || [],
            loading: false,
          });
        } catch (error) {
          console.error('Error filtering nodes:', error);
          set({
            error: error.response?.data?.message || 'Failed to filter nodes',
            loading: false,
          });
        }
      },

      fetchSnapshots: async () => {
        try {
          const snapshots = await graphService.getGraphSnapshots();
          set({ snapshots });
          return snapshots;
        } catch (error) {
          console.error('Error fetching snapshots:', error);
        }
      },

      saveSnapshot: async (name, description = '') => {
        try {
          const snapshot = await graphService.saveGraphSnapshot(name, description);
          set((state) => ({
            snapshots: [...state.snapshots, snapshot],
            currentSnapshot: snapshot,
          }));
          return snapshot;
        } catch (error) {
          console.error('Error saving snapshot:', error);
          throw error;
        }
      },

      loadSnapshot: async (snapshotId) => {
        set({ loading: true });
        
        try {
          const data = await graphService.loadGraphSnapshot(snapshotId);
          set({
            nodes: data.nodes || [],
            links: data.links || [],
            currentSnapshot: data,
            loading: false,
          });
          return data;
        } catch (error) {
          console.error('Error loading snapshot:', error);
          set({ loading: false });
          throw error;
        }
      },

      // Graph Updates
      addNode: (node) =>
        set((state) => ({
          nodes: [...state.nodes, node],
        })),

      updateNode: (nodeId, updates) =>
        set((state) => ({
          nodes: state.nodes.map((n) =>
            n.id === nodeId ? { ...n, ...updates } : n
          ),
        })),

      removeNode: (nodeId) =>
        set((state) => ({
          nodes: state.nodes.filter((n) => n.id !== nodeId),
          links: state.links.filter(
            (l) => l.source !== nodeId && l.target !== nodeId
          ),
          selectedNode: state.selectedNode?.id === nodeId ? null : state.selectedNode,
        })),

      addLink: (link) =>
        set((state) => ({
          links: [...state.links, link],
        })),

      removeLink: (linkId) =>
        set((state) => ({
          links: state.links.filter((l) => l.id !== linkId),
        })),

      // Node highlighting
      highlightNode: (nodeId) => {
        const { nodes, links } = get();
        
        if (!nodeId) {
          set({ highlightedNode: null });
          return;
        }
        
        const node = nodes.find((n) => n.id === nodeId);
        set({ highlightedNode: node });
      },

      // Clear state
      clearSelectedNode: () => set({ selectedNode: null }),
      
      clearHighlightedNode: () => set({ highlightedNode: null }),
      
      clearError: () => set({ error: null }),
      
      clearSearch: () => set({ searchQuery: '', searchResults: [] }),
      
      reset: () => set(initialState),
    }),
    { name: 'GraphStore' }
  )
);

export default graphStore;

// Helper functions
export const getNodeColor = (node) => {
  const riskScore = node.risk_score || 0;
  
  if (riskScore >= 80) return RISK_LEVELS.CRITICAL;
  if (riskScore >= 60) return RISK_LEVELS.HIGH;
  if (riskScore >= 40) return RISK_LEVELS.MEDIUM;
  return RISK_LEVELS.LOW;
};

export const getNodeSize = (node, baseSize = 10) => {
  const riskScore = node.risk_score || 0;
  const connections = node.connections || 1;
  return baseSize + (riskScore / 10) + Math.log(connections) * 3;
};
