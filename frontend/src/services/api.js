// API client service using axios
import axios from 'axios';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API] Response:`, response.data);
    }
    
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error);
    
    // Handle specific error cases
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - redirect to login or clear token
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          console.warn('[API] Access forbidden');
          break;
        case 404:
          console.warn('[API] Resource not found');
          break;
        case 429:
          console.warn('[API] Rate limit exceeded');
          break;
        case 500:
          console.error('[API] Server error');
          break;
        default:
          console.error(`[API] HTTP ${status}:`, data?.message || 'Unknown error');
      }
    } else if (error.request) {
      console.error('[API] Network error - no response received');
    }
    
    return Promise.reject(error);
  }
);

// Graph API methods
export const graphAPI = {
  // Get complete graph data (nodes and edges)
  getGraph: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/graph?${params}`);
    return response.data;
  },

  // Get graph statistics
  getGraphStats: async () => {
    const response = await apiClient.get('/graph/stats');
    return response.data;
  },

  // Export graph data
  exportGraph: async (format = 'json') => {
    const response = await apiClient.post('/graph/export', { format }, {
      responseType: format === 'json' ? 'json' : 'blob'
    });
    return response.data;
  },

  // Update graph data
  updateGraph: async (nodes, edges) => {
    const response = await apiClient.put('/graph', { nodes, edges });
    return response.data;
  },

  // Clear graph data
  clearGraph: async () => {
    const response = await apiClient.delete('/graph');
    return response.data;
  }
};

// Entity API methods
export const entityAPI = {
  // Get all entities
  getEntities: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/entities?${params}`);
    return response.data;
  },

  // Get single entity by ID
  getEntity: async (id) => {
    const response = await apiClient.get(`/entities/${id}`);
    return response.data;
  },

  // Create new entity
  createEntity: async (entityData) => {
    const response = await apiClient.post('/entities', entityData);
    return response.data;
  },

  // Update entity
  updateEntity: async (id, entityData) => {
    const response = await apiClient.put(`/entities/${id}`, entityData);
    return response.data;
  },

  // Delete entity
  deleteEntity: async (id) => {
    const response = await apiClient.delete(`/entities/${id}`);
    return response.data;
  },

  // Search entities
  searchEntities: async (query, filters = {}) => {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await apiClient.get(`/entities/search?${params}`);
    return response.data;
  },

  // Get entities by type
  getEntitiesByType: async (type) => {
    const response = await apiClient.get(`/entities/type/${type}`);
    return response.data;
  },

  // Bulk create entities
  bulkCreateEntities: async (entities) => {
    const response = await apiClient.post('/entities/bulk', { entities });
    return response.data;
  },

  // Bulk update entities
  bulkUpdateEntities: async (entities) => {
    const response = await apiClient.put('/entities/bulk', { entities });
    return response.data;
  },

  // Bulk delete entities
  bulkDeleteEntities: async (ids) => {
    const response = await apiClient.delete('/entities/bulk', { data: { ids } });
    return response.data;
  }
};

// Relationship API methods
export const relationshipAPI = {
  // Get all relationships
  getRelationships: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/relationships?${params}`);
    return response.data;
  },

  // Get single relationship by ID
  getRelationship: async (id) => {
    const response = await apiClient.get(`/relationships/${id}`);
    return response.data;
  },

  // Create new relationship
  createRelationship: async (relationshipData) => {
    const response = await apiClient.post('/relationships', relationshipData);
    return response.data;
  },

  // Update relationship
  updateRelationship: async (id, relationshipData) => {
    const response = await apiClient.put(`/relationships/${id}`, relationshipData);
    return response.data;
  },

  // Delete relationship
  deleteRelationship: async (id) => {
    const response = await apiClient.delete(`/relationships/${id}`);
    return response.data;
  },

  // Get relationships for entity
  getEntityRelationships: async (entityId) => {
    const response = await apiClient.get(`/entities/${entityId}/relationships`);
    return response.data;
  },

  // Search relationships
  searchRelationships: async (query, filters = {}) => {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await apiClient.get(`/relationships/search?${params}`);
    return response.data;
  },

  // Bulk create relationships
  bulkCreateRelationships: async (relationships) => {
    const response = await apiClient.post('/relationships/bulk', { relationships });
    return response.data;
  }
};

// Collection API methods
export const collectionAPI = {
  // Start collection task
  startCollection: async (target, types, options = {}) => {
    const response = await apiClient.post('/collection/start', {
      target,
      types,
      ...options
    });
    return response.data;
  },

  // Get collection task status
  getCollectionStatus: async (taskId) => {
    const response = await apiClient.get(`/collection/tasks/${taskId}`);
    return response.data;
  },

  // Get collection results
  getCollectionResults: async (taskId) => {
    const response = await apiClient.get(`/collection/tasks/${taskId}/results`);
    return response.data;
  },

  // Get all collection tasks
  getCollectionTasks: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/collection/tasks?${params}`);
    return response.data;
  },

  // Cancel collection task
  cancelCollection: async (taskId) => {
    const response = await apiClient.post(`/collection/tasks/${taskId}/cancel`);
    return response.data;
  },

  // Pause collection task
  pauseCollection: async (taskId) => {
    const response = await apiClient.post(`/collection/tasks/${taskId}/pause`);
    return response.data;
  },

  // Resume collection task
  resumeCollection: async (taskId) => {
    const response = await apiClient.post(`/collection/tasks/${taskId}/resume`);
    return response.data;
  }
};

// Health/Status API methods
export const healthAPI = {
  // Get system health status
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Get detailed system status
  getSystemStatus: async () => {
    const response = await apiClient.get('/health/detailed');
    return response.data;
  },

  // Get database status
  getDatabaseStatus: async () => {
    const response = await apiClient.get('/health/database');
    return response.data;
  },

  // Get Neo4j status
  getNeo4jStatus: async () => {
    const response = await apiClient.get('/health/neo4j');
    return response.data;
  },

  // Get Redis status
  getRedisStatus: async () => {
    const response = await apiClient.get('/health/redis');
    return response.data;
  }
};

// Target API methods
export const targetAPI = {
  // Get all targets
  getTargets: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/targets?${params}`);
    return response.data;
  },

  // Get single target by ID
  getTarget: async (id) => {
    const response = await apiClient.get(`/targets/${id}`);
    return response.data;
  },

  // Create new target
  createTarget: async (targetData) => {
    const response = await apiClient.post('/targets', targetData);
    return response.data;
  },

  // Update target
  updateTarget: async (id, targetData) => {
    const response = await apiClient.put(`/targets/${id}`, targetData);
    return response.data;
  },

  // Delete target
  deleteTarget: async (id) => {
    const response = await apiClient.delete(`/targets/${id}`);
    return response.data;
  },

  // Get target history
  getTargetHistory: async (id) => {
    const response = await apiClient.get(`/targets/${id}/history`);
    return response.data;
  }
};

// Analytics API methods
export const analyticsAPI = {
  // Get risk statistics
  getRiskStats: async () => {
    const response = await apiClient.get('/analytics/risk');
    return response.data;
  },

  // Get entity type statistics
  getEntityTypeStats: async () => {
    const response = await apiClient.get('/analytics/entity-types');
    return response.data;
  },

  // Get collection statistics
  getCollectionStats: async () => {
    const response = await apiClient.get('/analytics/collection');
    return response.data;
  },

  // Get graph metrics
  getGraphMetrics: async () => {
    const response = await apiClient.get('/analytics/graph');
    return response.data;
  }
};

// Generic API utility methods
export const apiUtils = {
  // Test API connectivity
  testConnection: async () => {
    try {
      await apiClient.get('/health');
      return { connected: true, error: null };
    } catch (error) {
      return { 
        connected: false, 
        error: error.message || 'Connection failed' 
      };
    }
  },

  // Get current base URL
  getBaseURL: () => apiClient.defaults.baseURL,

  // Set authentication token
  setAuthToken: (token) => {
    if (token) {
      localStorage.setItem('authToken', token);
      apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      localStorage.removeItem('authToken');
      delete apiClient.defaults.headers.Authorization;
    }
  },

  // Clear authentication
  clearAuth: () => {
    localStorage.removeItem('authToken');
    delete apiClient.defaults.headers.Authorization;
  }
};

// Export the main API client
export default apiClient;