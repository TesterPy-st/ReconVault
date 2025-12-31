// ReconVault Entity Service API

import api from './api';

const ENTITY_ENDPOINT = '/entities';

// Get all entities with pagination and filters
export const getEntities = async (params = {}) => {
  const defaultParams = {
    page: 1,
    limit: 50,
    sort_by: 'risk_score',
    sort_order: 'desc',
    ...params,
  };
  
  const response = await api.get(ENTITY_ENDPOINT, { params: defaultParams });
  return response.data;
};

// Get single entity by ID
export const getEntity = async (id) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/${id}`);
  return response.data;
};

// Create new entity
export const createEntity = async (data) => {
  const response = await api.post(ENTITY_ENDPOINT, data);
  return response.data;
};

// Update entity
export const updateEntity = async (id, data) => {
  const response = await api.put(`${ENTITY_ENDPOINT}/${id}`, data);
  return response.data;
};

// Partial update entity
export const patchEntity = async (id, data) => {
  const response = await api.patch(`${ENTITY_ENDPOINT}/${id}`, data);
  return response.data;
};

// Delete entity
export const deleteEntity = async (id) => {
  const response = await api.delete(`${ENTITY_ENDPOINT}/${id}`);
  return response.data;
};

// Get entity relationships
export const getEntityRelationships = async (id, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/${id}/relationships`, { params });
  return response.data;
};

// Get entity intelligence
export const getEntityIntelligence = async (id, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/${id}/intelligence`, { params });
  return response.data;
};

// Get entity findings
export const getEntityFindings = async (id, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/${id}/findings`, { params });
  return response.data;
};

// Search entities
export const searchEntities = async (query, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/search`, {
    params: { q: query, ...params },
  });
  return response.data;
};

// Get entities by type
export const getEntitiesByType = async (type, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/type/${type}`, { params });
  return response.data;
};

// Get entities by risk level
export const getEntitiesByRiskLevel = async (level, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/risk/${level}`, { params });
  return response.data;
};

// Get high-risk entities
export const getHighRiskEntities = async (params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/high-risk`, { params });
  return response.data;
};

// Add intelligence to entity
export const addEntityIntelligence = async (entityId, data) => {
  const response = await api.post(`${ENTITY_ENDPOINT}/${entityId}/intelligence`, data);
  return response.data;
};

// Add finding to entity
export const addEntityFinding = async (entityId, data) => {
  const response = await api.post(`${ENTITY_ENDPOINT}/${entityId}/findings`, data);
  return response.data;
};

// Get entity timeline
export const getEntityTimeline = async (id, params = {}) => {
  const response = await api.get(`${ENTITY_ENDPOINT}/${id}/timeline`, { params });
  return response.data;
};

// Bulk update entities
export const bulkUpdateEntities = async (ids, data) => {
  const response = await api.patch(ENTITY_ENDPOINT, { ids, data });
  return response.data;
};

// Bulk delete entities
export const bulkDeleteEntities = async (ids) => {
  const response = await api.delete(ENTITY_ENDPOINT, { data: { ids } });
  return response.data;
};

// Get entity statistics
export const getEntityStats = async () => {
  const response = await api.get(`${ENTITY_ENDPOINT}/stats`);
  return response.data;
};

// Get entity types distribution
export const getEntityTypeDistribution = async () => {
  const response = await api.get(`${ENTITY_ENDPOINT}/types/distribution`);
  return response.data;
};
