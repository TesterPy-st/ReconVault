// ReconVault Entity Store - State Management with Zustand

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as entityService from '../services/entityService';
import * as websocketService from '../services/websocketService';

const initialState = {
  entities: [],
  selectedEntity: null,
  highlightedEntity: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 50,
    total: 0,
    totalPages: 0,
  },
  filters: {
    type: null,
    riskLevel: null,
    search: '',
    sortBy: 'risk_score',
    sortOrder: 'desc',
  },
  stats: {
    total: 0,
    byType: {},
    byRiskLevel: {
      low: 0,
      medium: 0,
      high: 0,
      critical: 0,
    },
  },
  relationships: [],
  intelligence: [],
  findings: [],
  entityTypes: [],
  wsConnected: false,
};

const entityStore = create(
  devtools(
    (set, get) => ({
      ...initialState,

      // WebSocket setup
      initWebSocket: () => {
        const wsConnected = get().wsConnected;
        
        if (!wsConnected) {
          wsService.connect('/ws');
          
          wsService.on(WS_EVENTS.CONNECTION, (data) => {
            set({ wsConnected: data.status === 'connected' });
          });
          
          wsService.on(WS_EVENTS.ENTITY_DISCOVERED, (entity) => {
            set((state) => ({
              entities: [entity, ...state.entities],
              pagination: {
                ...state.pagination,
                total: state.pagination.total + 1,
              },
            }));
          });
          
          wsService.on(WS_EVENTS.ENTITY_UPDATED, (updatedEntity) => {
            set((state) => ({
              entities: state.entities.map((e) =>
                e.id === updatedEntity.id ? updatedEntity : e
              ),
              selectedEntity:
                state.selectedEntity?.id === updatedEntity.id
                  ? updatedEntity
                  : state.selectedEntity,
            }));
          });
          
          wsService.on(WS_EVENTS.RELATIONSHIP_FOUND, (relationship) => {
            set((state) => ({
              relationships: [...state.relationships, relationship],
            }));
          });
          
          wsService.on(WS_EVENTS.INTELLIGENCE_FOUND, (intelligence) => {
            set((state) => ({
              intelligence: [intelligence, ...state.intelligence],
            }));
          });
          
          wsService.on(WS_EVENTS.RISK_SCORE, ({ entityId, score }) => {
            set((state) => ({
              entities: state.entities.map((e) =>
                e.id === entityId ? { ...e, risk_score: score } : e
              ),
            }));
          });
        }
      },

      disconnectWebSocket: () => {
        wsService.disconnect();
        set({ wsConnected: false });
      },

      // Basic Actions
      setEntities: (entities) => set({ entities }),
      
      setSelectedEntity: (entity) => set({ selectedEntity: entity }),
      
      setHighlightedEntity: (entity) => set({ highlightedEntity: entity }),
      
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
      
      setStats: (stats) => set({ stats }),
      
      setRelationships: (relationships) => set({ relationships }),
      
      setIntelligence: (intelligence) => set({ intelligence }),
      
      setFindings: (findings) => set({ findings }),
      
      setEntityTypes: (types) => set({ entityTypes: types }),

      // Async Actions
      fetchEntities: async (params = {}) => {
        const { filters, pagination } = get();
        set({ loading: true, error: null });
        
        try {
          const queryParams = {
            ...filters,
            ...pagination,
            ...params,
          };
          
          const response = await entityService.getEntities(queryParams);
          
          set({
            entities: response.data || response.results || response.items || [],
            pagination: {
              page: response.page || 1,
              limit: response.limit || 50,
              total: response.total || 0,
              totalPages: response.totalPages || Math.ceil((response.total || 0) / (response.limit || 50)),
            },
            loading: false,
          });
        } catch (error) {
          console.error('Error fetching entities:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch entities',
            loading: false,
          });
        }
      },

      fetchEntity: async (id) => {
        set({ loading: true, error: null });
        
        try {
          const entity = await entityService.getEntity(id);
          set({ selectedEntity: entity, loading: false });
          
          // Fetch related data
          const [relationships, intelligence, findings] = await Promise.all([
            entityService.getEntityRelationships(id),
            entityService.getEntityIntelligence(id),
            entityService.getEntityFindings(id),
          ]);
          
          set({
            relationships: relationships.data || [],
            intelligence: intelligence.data || [],
            findings: findings.data || [],
          });
          
          return entity;
        } catch (error) {
          console.error('Error fetching entity:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch entity',
            loading: false,
          });
          throw error;
        }
      },

      createEntity: async (data) => {
        set({ loading: true, error: null });
        
        try {
          const newEntity = await entityService.createEntity(data);
          set((state) => ({
            entities: [newEntity, ...state.entities],
            loading: false,
          }));
          return newEntity;
        } catch (error) {
          console.error('Error creating entity:', error);
          set({
            error: error.response?.data?.message || 'Failed to create entity',
            loading: false,
          });
          throw error;
        }
      },

      updateEntity: async (id, data) => {
        set({ loading: true, error: null });
        
        try {
          const updatedEntity = await entityService.updateEntity(id, data);
          set((state) => ({
            entities: state.entities.map((e) =>
              e.id === id ? updatedEntity : e
            ),
            selectedEntity:
              state.selectedEntity?.id === id
                ? updatedEntity
                : state.selectedEntity,
            loading: false,
          }));
          return updatedEntity;
        } catch (error) {
          console.error('Error updating entity:', error);
          set({
            error: error.response?.data?.message || 'Failed to update entity',
            loading: false,
          });
          throw error;
        }
      },

      deleteEntity: async (id) => {
        set({ loading: true, error: null });
        
        try {
          await entityService.deleteEntity(id);
          set((state) => ({
            entities: state.entities.filter((e) => e.id !== id),
            selectedEntity:
              state.selectedEntity?.id === id ? null : state.selectedEntity,
            loading: false,
          }));
        } catch (error) {
          console.error('Error deleting entity:', error);
          set({
            error: error.response?.data?.message || 'Failed to delete entity',
            loading: false,
          });
          throw error;
        }
      },

      fetchEntityRelationships: async (id, params = {}) => {
        try {
          const response = await entityService.getEntityRelationships(id, params);
          set({ relationships: response.data || response || [] });
          return response;
        } catch (error) {
          console.error('Error fetching relationships:', error);
          throw error;
        }
      },

      fetchEntityIntelligence: async (id, params = {}) => {
        try {
          const response = await entityService.getEntityIntelligence(id, params);
          set({ intelligence: response.data || response || [] });
          return response;
        } catch (error) {
          console.error('Error fetching intelligence:', error);
          throw error;
        }
      },

      fetchEntityFindings: async (id, params = {}) => {
        try {
          const response = await entityService.getEntityFindings(id, params);
          set({ findings: response.data || response || [] });
          return response;
        } catch (error) {
          console.error('Error fetching findings:', error);
          throw error;
        }
      },

      fetchHighRiskEntities: async (params = {}) => {
        set({ loading: true, error: null });
        
        try {
          const response = await entityService.getHighRiskEntities(params);
          set({
            entities: response.data || response.results || [],
            loading: false,
          });
        } catch (error) {
          console.error('Error fetching high risk entities:', error);
          set({
            error: error.response?.data?.message || 'Failed to fetch high risk entities',
            loading: false,
          });
        }
      },

      fetchStats: async () => {
        try {
          const stats = await entityService.getEntityStats();
          set({ stats });
          return stats;
        } catch (error) {
          console.error('Error fetching entity stats:', error);
        }
      },

      searchEntities: async (query) => {
        if (!query || query.length < 2) {
          set({ entities: [], filters: { ...get().filters, search: '' } });
          return;
        }
        
        set({ loading: true, filters: { ...get().filters, search: query } });
        
        try {
          const response = await entityService.searchEntities(query);
          set({
            entities: response.data || response.results || [],
            loading: false,
          });
        } catch (error) {
          console.error('Error searching entities:', error);
          set({
            error: error.response?.data?.message || 'Search failed',
            loading: false,
          });
        }
      },

      // Entity actions
      addIntelligence: async (entityId, data) => {
        try {
          const intelligence = await entityService.addEntityIntelligence(entityId, data);
          set((state) => ({
            intelligence: [intelligence, ...state.intelligence],
          }));
          return intelligence;
        } catch (error) {
          console.error('Error adding intelligence:', error);
          throw error;
        }
      },

      addFinding: async (entityId, data) => {
        try {
          const finding = await entityService.addEntityFinding(entityId, data);
          set((state) => ({
            findings: [finding, ...state.findings],
          }));
          return finding;
        } catch (error) {
          console.error('Error adding finding:', error);
          throw error;
        }
      },

      // Clear state
      clearSelectedEntity: () =>
        set({
          selectedEntity: null,
          relationships: [],
          intelligence: [],
          findings: [],
        }),
      
      clearHighlightedEntity: () => set({ highlightedEntity: null }),
      
      clearError: () => set({ error: null }),
      
      resetFilters: () =>
        set({
          filters: initialState.filters,
        }),

      reset: () => set(initialState),
    }),
    { name: 'EntityStore' }
  )
);

export default entityStore;
