// ReconVault API Configuration and Axios Instance

import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracing
    config.headers['X-Request-ID'] = generateRequestId();
    
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status}:`, response.config.url);
    return response;
  },
  (error) => {
    const { response } = error;
    
    if (response) {
      console.error(`[API] Error ${response.status}:`, response.config?.url, response.data);
      
      // Handle specific error codes
      switch (response.status) {
        case 401:
          // Handle unauthorized - redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          console.error('[API] Access forbidden');
          break;
        case 404:
          console.error('[API] Resource not found');
          break;
        case 429:
          console.warn('[API] Rate limited');
          break;
        case 500:
          console.error('[API] Server error');
          break;
        default:
          console.error('[API] Unknown error');
      }
    } else if (error.request) {
      console.error('[API] Network error - no response received');
    } else {
      console.error('[API] Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default api;

// API helper functions
export const get = (url, params) => api.get(url, { params });
export const post = (url, data) => api.post(url, data);
export const put = (url, data) => api.put(url, data);
export const patch = (url, data) => api.patch(url, data);
export const del = (url) => api.delete(url);
