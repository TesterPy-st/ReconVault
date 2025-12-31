// ReconVault Graph Service API

import api from './api';

const GRAPH_ENDPOINT = '/graph';

// Get full graph data
export const getGraphData = async (params = {}) => {
  const response = await api.get(GRAPH_ENDPOINT, { params });
  return response.data;
};

// Get graph data for specific target
export const getTargetGraphData = async (targetId, params = {}) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/target/${targetId}`, { params });
  return response.data;
};

// Get graph data for specific entity
export const getEntityGraphData = async (entityId, depth = 2) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/entity/${entityId}`, {
    params: { depth },
  });
  return response.data;
};

// Get graph statistics
export const getGraphStats = async () => {
  const response = await api.get(`${GRAPH_ENDPOINT}/stats`);
  return response.data;
};

// Get graph node details
export const getNodeDetails = async (nodeId) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/node/${nodeId}`);
  return response.data;
};

// Get graph edge details
export const getEdgeDetails = async (edgeId) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/edge/${edgeId}`);
  return response.data;
};

// Search graph nodes
export const searchGraphNodes = async (query, params = {}) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/search`, {
    params: { q: query, ...params },
  });
  return response.data;
};

// Filter graph nodes
export const filterGraphNodes = async (filters = {}) => {
  const response = await api.post(`${GRAPH_ENDPOINT}/filter`, filters);
  return response.data;
};

// Get graph clusters
export const getGraphClusters = async (params = {}) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/clusters`, { params });
  return response.data;
};

// Get graph paths between nodes
export const getGraphPaths = async (sourceId, targetId, maxDepth = 5) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/paths`, {
    params: { source: sourceId, target: targetId, max_depth: maxDepth },
  });
  return response.data;
};

// Get shortest path between nodes
export const getShortestPath = async (sourceId, targetId) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/shortest-path`, {
    params: { source: sourceId, target: targetId },
  });
  return response.data;
};

// Get central nodes (most connected)
export const getCentralNodes = async (params = {}) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/central`, { params });
  return response.data;
};

// Get graph communities
export const getGraphCommunities = async () => {
  const response = await api.get(`${GRAPH_ENDPOINT}/communities`);
  return response.data;
};

// Export graph data
export const exportGraphData = async (format = 'json', params = {}) => {
  const response = await api.get(`${GRAPH_ENDPOINT}/export`, {
    params: { format, ...params },
    responseType: format === 'json' ? 'json' : 'blob',
  });
  return response.data;
};

// Save graph snapshot
export const saveGraphSnapshot = async (name, description = '') => {
  const response = await api.post(`${GRAPH_ENDPOINT}/snapshot`, { name, description });
  return response.data;
};

// Get saved snapshots
export const getGraphSnapshots = async () => {
  const response = await api.get(`${GRAPH_ENDPOINT}/snapshots`);
  return response.data;
};

// Load graph snapshot
export const loadGraphSnapshot = async (snapshotId) => {
  const response = await api.post(`${GRAPH_ENDPOINT}/snapshot/${snapshotId}/load`);
  return response.data;
};

// Update graph layout
export const updateGraphLayout = async (layoutType = 'force') => {
  const response = await api.post(`${GRAPH_ENDPOINT}/layout`, { type: layoutType });
  return response.data;
};

// Get graph layout options
export const getLayoutOptions = async () => {
  const response = await api.get(`${GRAPH_ENDPOINT}/layout/options`);
  return response.data;
};
