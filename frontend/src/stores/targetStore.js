// ReconVault Target Store - State Management with Zustand

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import * as targetService from '../services/targetService';
import { TARGET_STATUS } from '../utils/constants';

const initialState = {
  targets: [],
  selectedTarget: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
  },
  filters: {
    status: null,
    type: null,
    search: '',
    sortBy: 'created_at',
    sortOrder: 'desc',
  },
  stats: {
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
  },
};

const targetStore = create(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Actions
        setTargets: (targets) => set({ targets }),
        
        setSelectedTarget: (target) => set({ selectedTarget: target }),
        
        setLoading: (loading) => set({ loading }),
        
        setError: (error) => set({ error }),
        
        setPagination: (pagination) =>
          set((state) => ({
            pagination: { ...state.pagination, ...pagination },
          })),
        
        setFilters: (filters) =>
          set((state) => ({
            filters: { ...state.filters, ...filters },
          })),
        
        resetFilters: () =>
          set({
            filters: initialState.filters,
          }),

        setStats: (stats) => set({ stats }),

        // Async Actions
        fetchTargets: async (params = {}) => {
          const { filters, pagination } = get();
          set({ loading: true, error: null });
          
          try {
            const queryParams = {
              ...filters,
              ...pagination,
              ...params,
            };
            
            const response = await targetService.getTargets(queryParams);
            
            set({
              targets: response.data || response.results || response.items || [],
              pagination: {
                page: response.page || 1,
                limit: response.limit || 20,
                total: response.total || 0,
                totalPages: response.totalPages || Math.ceil((response.total || 0) / (response.limit || 20)),
              },
              loading: false,
            });
          } catch (error) {
            console.error('Error fetching targets:', error);
            set({
              error: error.response?.data?.message || 'Failed to fetch targets',
              loading: false,
            });
          }
        },

        fetchTarget: async (id) => {
          set({ loading: true, error: null });
          
          try {
            const target = await targetService.getTarget(id);
            set({ selectedTarget: target, loading: false });
            return target;
          } catch (error) {
            console.error('Error fetching target:', error);
            set({
              error: error.response?.data?.message || 'Failed to fetch target',
              loading: false,
            });
            throw error;
          }
        },

        createTarget: async (data) => {
          set({ loading: true, error: null });
          
          try {
            const newTarget = await targetService.createTarget(data);
            set((state) => ({
              targets: [newTarget, ...state.targets],
              pagination: {
                ...state.pagination,
                total: state.pagination.total + 1,
              },
              loading: false,
            }));
            return newTarget;
          } catch (error) {
            console.error('Error creating target:', error);
            set({
              error: error.response?.data?.message || 'Failed to create target',
              loading: false,
            });
            throw error;
          }
        },

        updateTarget: async (id, data) => {
          set({ loading: true, error: null });
          
          try {
            const updatedTarget = await targetService.updateTarget(id, data);
            set((state) => ({
              targets: state.targets.map((t) =>
                t.id === id ? updatedTarget : t
              ),
              selectedTarget:
                state.selectedTarget?.id === id
                  ? updatedTarget
                  : state.selectedTarget,
              loading: false,
            }));
            return updatedTarget;
          } catch (error) {
            console.error('Error updating target:', error);
            set({
              error: error.response?.data?.message || 'Failed to update target',
              loading: false,
            });
            throw error;
          }
        },

        deleteTarget: async (id) => {
          set({ loading: true, error: null });
          
          try {
            await targetService.deleteTarget(id);
            set((state) => ({
              targets: state.targets.filter((t) => t.id !== id),
              selectedTarget:
                state.selectedTarget?.id === id ? null : state.selectedTarget,
              pagination: {
                ...state.pagination,
                total: state.pagination.total - 1,
              },
              loading: false,
            }));
          } catch (error) {
            console.error('Error deleting target:', error);
            set({
              error: error.response?.data?.message || 'Failed to delete target',
              loading: false,
            });
            throw error;
          }
        },

        startRecon: async (id) => {
          try {
            await targetService.startReconnaissance(id);
            set((state) => ({
              targets: state.targets.map((t) =>
                t.id === id ? { ...t, status: TARGET_STATUS.PROCESSING } : t
              ),
            }));
          } catch (error) {
            console.error('Error starting reconnaissance:', error);
            throw error;
          }
        },

        stopRecon: async (id) => {
          try {
            await targetService.stopReconnaissance(id);
            set((state) => ({
              targets: state.targets.map((t) =>
                t.id === id ? { ...t, status: TARGET_STATUS.CANCELLED } : t
              ),
            }));
          } catch (error) {
            console.error('Error stopping reconnaissance:', error);
            throw error;
          }
        },

        fetchStats: async () => {
          try {
            const stats = await targetService.getTargetStats();
            set({ stats });
          } catch (error) {
            console.error('Error fetching stats:', error);
          }
        },

        searchTargets: async (query) => {
          set({ loading: true, error: null });
          
          try {
            const response = await targetService.searchTargets(query);
            set({
              targets: response.data || response.results || [],
              loading: false,
            });
          } catch (error) {
            console.error('Error searching targets:', error);
            set({
              error: error.response?.data?.message || 'Search failed',
              loading: false,
            });
          }
        },

        clearSelectedTarget: () => set({ selectedTarget: null }),
        
        clearError: () => set({ error: null }),
        
        reset: () => set(initialState),
      }),
      {
        name: 'target-store',
        partialize: (state) => ({
          filters: state.filters,
        }),
      }
    ),
    { name: 'TargetStore' }
  )
);

export default targetStore;
