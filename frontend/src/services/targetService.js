// ReconVault Target Service API

import api from './api';

const TARGET_ENDPOINT = '/targets';

// Get all targets with pagination and filters
export const getTargets = async (params = {}) => {
  const defaultParams = {
    page: 1,
    limit: 20,
    sort_by: 'created_at',
    sort_order: 'desc',
    ...params,
  };
  
  const response = await api.get(TARGET_ENDPOINT, { params: defaultParams });
  return response.data;
};

// Get single target by ID
export const getTarget = async (id) => {
  const response = await api.get(`${TARGET_ENDPOINT}/${id}`);
  return response.data;
};

// Create new target
export const createTarget = async (data) => {
  const response = await api.post(TARGET_ENDPOINT, data);
  return response.data;
};

// Update target
export const updateTarget = async (id, data) => {
  const response = await api.put(`${TARGET_ENDPOINT}/${id}`, data);
  return response.data;
};

// Partial update target
export const patchTarget = async (id, data) => {
  const response = await api.patch(`${TARGET_ENDPOINT}/${id}`, data);
  return response.data;
};

// Delete target
export const deleteTarget = async (id) => {
  const response = await api.delete(`${TARGET_ENDPOINT}/${id}`);
  return response.data;
};

// Start reconnaissance on target
export const startReconnaissance = async (id) => {
  const response = await api.post(`${TARGET_ENDPOINT}/${id}/recon`);
  return response.data;
};

// Stop reconnaissance on target
export const stopReconnaissance = async (id) => {
  const response = await api.post(`${TARGET_ENDPOINT}/${id}/stop`);
  return response.data;
};

// Get target entities
export const getTargetEntities = async (id, params = {}) => {
  const response = await api.get(`${TARGET_ENDPOINT}/${id}/entities`, { params });
  return response.data;
};

// Get target relationships
export const getTargetRelationships = async (id, params = {}) => {
  const response = await api.get(`${TARGET_ENDPOINT}/${id}/relationships`, { params });
  return response.data;
};

// Get target intelligence
export const getTargetIntelligence = async (id, params = {}) => {
  const response = await api.get(`${TARGET_ENDPOINT}/${id}/intelligence`, { params });
  return response.data;
};

// Get target graph data
export const getTargetGraph = async (id) => {
  const response = await api.get(`${TARGET_ENDPOINT}/${id}/graph`);
  return response.data;
};

// Search targets
export const searchTargets = async (query, params = {}) => {
  const response = await api.get(`${TARGET_ENDPOINT}/search`, {
    params: { q: query, ...params },
  });
  return response.data;
};

// Bulk delete targets
export const bulkDeleteTargets = async (ids) => {
  const response = await api.delete(TARGET_ENDPOINT, { data: { ids } });
  return response.data;
};

// Export targets
export const exportTargets = async (params = {}, format = 'json') => {
  const response = await api.get(`${TARGET_ENDPOINT}/export`, {
    params: { format, ...params },
    responseType: format === 'json' ? 'json' : 'blob',
  });
  return response.data;
};

// Get target statistics
export const getTargetStats = async () => {
  const response = await api.get(`${TARGET_ENDPOINT}/stats`);
  return response.data;
};

// Get recent targets
export const getRecentTargets = async (limit = 5) => {
  const response = await api.get(`${TARGET_ENDPOINT}/recent`, { params: { limit } });
  return response.data;
};
