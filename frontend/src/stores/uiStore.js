// ReconVault UI Store - State Management with Zustand

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { TOAST_DURATION, TOAST_POSITIONS } from '../utils/constants';

const initialState = {
  // Theme
  theme: 'dark',
  
  // Sidebar
  sidebarOpen: true,
  sidebarCollapsed: false,
  sidebarMobileOpen: false,
  
  // Modals
  activeModal: null,
  modalData: null,
  
  // Toast notifications
  toasts: [],
  
  // Loading states
  globalLoading: false,
  loadingMessage: '',
  
  // Entity panel
  entityPanelOpen: false,
  selectedEntity: null,
  
  // Settings
  settings: {
    notifications: true,
    sound: true,
    autoRefresh: true,
    refreshInterval: 30000,
    showRiskColors: true,
    showLabels: true,
    animations: true,
    compactMode: false,
  },
  
  // Search
  searchOpen: false,
  searchQuery: '',
  
  // Command palette
  commandPaletteOpen: false,
  
  // Keyboard shortcuts help
  showShortcuts: false,
};

const uiStore = create(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Theme
        setTheme: (theme) => set({ theme }),
        toggleTheme: () =>
          set((state) => ({
            theme: state.theme === 'dark' ? 'light' : 'dark',
          })),

        // Sidebar
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        setSidebarMobileOpen: (open) => set({ sidebarMobileOpen: open }),
        toggleSidebar: () =>
          set((state) => ({
            sidebarOpen: !state.sidebarOpen,
          })),
        toggleSidebarMobile: () =>
          set((state) => ({
            sidebarMobileOpen: !state.sidebarMobileOpen,
          })),

        // Modals
        openModal: (modalId, data = null) =>
          set({
            activeModal: modalId,
            modalData: data,
          }),
        closeModal: () =>
          set({
            activeModal: null,
            modalData: null,
          }),
        updateModalData: (data) =>
          set((state) => ({
            modalData: { ...state.modalData, ...data },
          })),

        // Toast notifications
        addToast: (toast) => {
          const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          const newToast = {
            id,
            duration: TOAST_DURATION,
            position: TOAST_POSITIONS.TOP_RIGHT,
            ...toast,
          };
          
          set((state) => ({
            toasts: [...state.toasts, newToast],
          }));
          
          // Auto-remove toast after duration
          if (newToast.duration > 0) {
            setTimeout(() => {
              get().removeToast(id);
            }, newToast.duration);
          }
          
          return id;
        },
        
        removeToast: (id) =>
          set((state) => ({
            toasts: state.toasts.filter((t) => t.id !== id),
          })),
        
        clearToasts: () => set({ toasts: [] }),
        
        showSuccess: (message, options = {}) =>
          get().addToast({
            type: 'success',
            message,
            ...options,
          }),
        
        showError: (message, options = {}) =>
          get().addToast({
            type: 'error',
            message,
            ...options,
          }),
        
        showWarning: (message, options = {}) =>
          get().addToast({
            type: 'warning',
            message,
            ...options,
          }),
        
        showInfo: (message, options = {}) =>
          get().addToast({
            type: 'info',
            message,
            ...options,
          }),

        // Loading states
        setGlobalLoading: (loading, message = '') =>
          set({
            globalLoading: loading,
            loadingMessage: loading ? message : '',
          }),
        
        setLoadingMessage: (message) =>
          set({ loadingMessage: message }),

        // Entity panel
        openEntityPanel: (entity) =>
          set({
            entityPanelOpen: true,
            selectedEntity: entity,
          }),
        
        closeEntityPanel: () =>
          set({
            entityPanelOpen: false,
            selectedEntity: null,
          }),
        
        updateSelectedEntity: (entity) =>
          set({ selectedEntity: entity }),

        // Settings
        updateSettings: (settings) =>
          set((state) => ({
            settings: { ...state.settings, ...settings },
          })),
        
        resetSettings: () =>
          set({ settings: initialState.settings }),

        // Search
        openSearch: () =>
          set({
            searchOpen: true,
            searchQuery: '',
          }),
        
        closeSearch: () =>
          set({
            searchOpen: false,
            searchQuery: '',
          }),
        
        setSearchQuery: (query) =>
          set({ searchQuery: query }),

        // Command palette
        openCommandPalette: () =>
          set({ commandPaletteOpen: true }),
        
        closeCommandPalette: () =>
          set({ commandPaletteOpen: false }),
        
        toggleCommandPalette: () =>
          set((state) => ({
            commandPaletteOpen: !state.commandPaletteOpen,
          })),

        // Keyboard shortcuts help
        setShowShortcuts: (show) =>
          set({ showShortcuts: show }),
        
        toggleShowShortcuts: () =>
          set((state) => ({
            showShortcuts: !state.showShortcuts,
          })),

        // Utility
        reset: () => set(initialState),
      }),
      {
        name: 'ui-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          settings: state.settings,
        }),
      }
    ),
    { name: 'UIStore' }
  )
);

export default uiStore;
