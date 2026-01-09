// ReconVault Main Application Component - Cyber Graph Visualization Interface
import React, { useEffect, useCallback, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';

import { useGraph } from './hooks/useGraph';
import { useWebSocket } from './hooks/useWebSocket';
import { useToast } from './components/Common/Toast';

// Layout Components
import TopHeader from './components/Panels/TopHeader';
import LeftSidebar from './components/Panels/LeftSidebar';
import RightSidebar from './components/Panels/RightSidebar';
import BottomStats from './components/Panels/BottomStats';
import GraphCanvas from './components/Graph/GraphCanvas';
import ComplianceDashboard from './components/Dashboard/ComplianceDashboard';

// Common Components
import SettingsPanel from './components/Common/SettingsPanel';
import ConnectionError from './components/Common/ConnectionError';
import ErrorBoundary from './components/Common/ErrorBoundary';

import { apiUtils, healthAPI } from './services/api';
import { mockGraphData } from './utils/mockGraphData';

// Import styles
import './styles/main.css';

function App() {
  // Layout state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(false);
  const [bottomStatsCollapsed, setBottomStatsCollapsed] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [activeView, setActiveView] = useState('graph'); // 'graph' or 'compliance'

  // Selection state
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);

  // Settings
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Graph sizing
  const graphContainerRef = useRef(null);
  const [graphContainerSize, setGraphContainerSize] = useState({ width: 800, height: 600 });

  // Toasts
  const toast = useToast();
  const { success, error: showError, loading: showLoading, updateToast } = toast;
  const ToastContainer = toast.ToastContainer;

  // Data
  const { nodes, edges, loading, error, filters, updateFilters, refreshGraph, performance } = useGraph();

  const {
    connected: wsConnected,
    addEventListener,
    url: wsUrl
  } = useWebSocket();

  // Backend connectivity state
  const apiBaseUrl = apiUtils.getBaseURL();
  const [backendState, setBackendState] = useState({
    connected: true,
    checking: true,
    lastError: null,
    nextRetryAt: null
  });

  const retryDelayRef = useRef(3000);
  const backendConnectedRef = useRef(true);

  // System status for the header
  const [systemStatus, setSystemStatus] = useState({
    backend: 'unknown',
    database: 'unknown',
    neo4j: 'unknown',
    redis: 'unknown'
  });

  const collectionHistory = useMemo(
    () => [
      {
        target: 'suspicious-domain.com',
        types: ['domain', 'web'],
        timestamp: '2024-01-20T15:30:00Z',
        status: 'completed'
      },
      {
        target: 'phishing-campaign.net',
        types: ['email', 'social'],
        timestamp: '2024-01-19T10:15:00Z',
        status: 'completed'
      },
      {
        target: 'malware-c2.example.com',
        types: ['domain', 'ip'],
        timestamp: '2024-01-18T14:22:00Z',
        status: 'completed'
      }
    ],
    []
  );

  const activeTasks = useMemo(
    () => [
      {
        id: 'task-1',
        target: 'new-threat-domain.com',
        type: 'domain',
        status: 'RUNNING',
        progress: 65,
        completed: 13,
        total: 20
      },
      {
        id: 'task-2',
        target: 'suspicious-ip-range',
        type: 'ip',
        status: 'RUNNING',
        progress: 30,
        completed: 6,
        total: 20
      }
    ],
    []
  );

  // Keep an up-to-date container size for the graph canvas
  useEffect(() => {
    if (!graphContainerRef.current) return;

    const element = graphContainerRef.current;

    const updateSize = () => {
      const rect = element.getBoundingClientRect();
      setGraphContainerSize({
        width: Math.max(0, Math.floor(rect.width)),
        height: Math.max(0, Math.floor(rect.height))
      });
    };

    updateSize();

    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', updateSize);
      return () => window.removeEventListener('resize', updateSize);
    }

    const resizeObserver = new ResizeObserver(() => updateSize());
    resizeObserver.observe(element);

    return () => resizeObserver.disconnect();
  }, [sidebarCollapsed, rightSidebarCollapsed, bottomStatsCollapsed, activeView]);

  const applyHealthToSystemStatus = useCallback((health) => {
    const overall = health?.overall_status;
    const services = health?.services || {};

    const dbStatus = services?.postgresql?.status;
    const neo4jStatus = services?.neo4j?.status;

    setSystemStatus({
      backend: overall || 'healthy',
      database: dbStatus === 'healthy' ? 'connected' : dbStatus || 'unknown',
      neo4j: neo4jStatus === 'healthy' ? 'connected' : neo4jStatus || 'unknown',
      redis: 'unknown'
    });
  }, []);

  const checkBackend = useCallback(
    async (manual = false) => {
      setBackendState((prev) => ({
        ...prev,
        checking: true
      }));

      const { connected, error: connectionError } = await apiUtils.testConnection();

      if (connected) {
        retryDelayRef.current = 3000;

        setBackendState({
          connected: true,
          checking: false,
          lastError: null,
          nextRetryAt: null
        });

        setSystemStatus((prev) => ({
          ...prev,
          backend: 'healthy'
        }));

        try {
          const health = await healthAPI.getSystemStatus();
          applyHealthToSystemStatus(health);
        } catch (healthError) {
          console.warn('[App] Failed to load detailed health status:', healthError);
        }

        if (!backendConnectedRef.current) {
          backendConnectedRef.current = true;
          refreshGraph();

          if (manual) {
            success('Backend reconnected');
          }
        }

        return 20000;
      }

      backendConnectedRef.current = false;

      const delay = retryDelayRef.current;
      retryDelayRef.current = Math.min(Math.round(delay * 1.5), 30000);

      setBackendState({
        connected: false,
        checking: false,
        lastError: connectionError,
        nextRetryAt: Date.now() + delay
      });

      setSystemStatus({
        backend: 'offline',
        database: 'unknown',
        neo4j: 'unknown',
        redis: 'unknown'
      });

      return delay;
    },
    [applyHealthToSystemStatus, refreshGraph, success]
  );

  // Auto-reconnect loop
  useEffect(() => {
    let cancelled = false;
    let timeout;

    const loop = async () => {
      const delay = await checkBackend(false);

      if (cancelled) return;
      timeout = setTimeout(loop, delay);
    };

    loop();

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [checkBackend]);

  // Force re-render for retry countdown display
  const [clockTick, setClockTick] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setClockTick((t) => t + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  const nextRetryInMs = useMemo(() => {
    if (!backendState.nextRetryAt) return null;
    return Math.max(0, backendState.nextRetryAt - Date.now());
  }, [backendState.nextRetryAt, clockTick]);

  const usingDemoData = !backendState.connected;

  const graphData = useMemo(() => {
    if (nodes.length > 0 || edges.length > 0) {
      return { nodes, edges };
    }
    return mockGraphData;
  }, [nodes, edges]);

  // WebSocket Event Listeners
  useEffect(() => {
    if (!wsConnected) return;

    const unsubscribeViolation = addEventListener('compliance_violation', (data) => {
      showError(`Compliance Violation: ${data.message} (${data.severity.toUpperCase()})`);
    });

    return () => {
      unsubscribeViolation?.();
    };
  }, [wsConnected, addEventListener, showError]);

  // Graph event handlers
  const handleNodeSelect = useCallback((node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  const handleEdgeSelect = useCallback((edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  const handleNodeHover = useCallback((node) => {
    console.log('Node hovered:', node?.id);
  }, []);

  const handleEdgeHover = useCallback((edge) => {
    console.log('Edge hovered:', edge?.id);
  }, []);

  // Collection handlers
  const handleStartCollection = useCallback(
    async (configOrTarget, types = []) => {
      const config =
        configOrTarget && typeof configOrTarget === 'object'
          ? configOrTarget
          : { target: configOrTarget, types };

      const toastId = showLoading('Starting intelligence collection...');

      try {
        await new Promise((resolve) => setTimeout(resolve, 2000));

        updateToast(toastId, {
          type: 'success',
          message: `Collection started for ${config.target || 'target'}`,
          duration: 5000
        });
      } catch (collectionError) {
        updateToast(toastId, {
          type: 'error',
          message: 'Failed to start collection: ' + collectionError.message,
          duration: 8000
        });
      }
    },
    [showLoading, updateToast]
  );

  const handleEntityAction = useCallback(
    (action, entity) => {
      switch (action) {
        case 'copy':
          navigator.clipboard.writeText(entity.value || entity.id);
          success('Entity copied to clipboard');
          break;
        case 'export':
          success('Entity exported successfully');
          break;
        case 'edit':
          showError('Edit functionality not implemented yet');
          break;
        case 'delete':
          showError('Delete functionality not implemented yet');
          break;
        default:
          console.log('Unknown entity action:', action);
      }
    },
    [success, showError]
  );

  const handleRelationshipAction = useCallback(
    (action) => {
      switch (action) {
        case 'edit':
          showError('Edit functionality not implemented yet');
          break;
        case 'delete':
          showError('Delete functionality not implemented yet');
          break;
        default:
          console.log('Unknown relationship action:', action);
      }
    },
    [showError]
  );

  // Header menu handlers
  const handleMenuAction = useCallback(
    (action) => {
      switch (action) {
        case 'compliance':
          setActiveView((prev) => (prev === 'compliance' ? 'graph' : 'compliance'));
          break;
        case 'home':
          setActiveView('graph');
          break;
        case 'export':
          success('Graph export functionality initiated');
          break;
        case 'settings':
          setSettingsOpen(true);
          break;
        case 'help':
          window.open('https://docs.reconvault.com', '_blank');
          break;
        case 'about':
          alert('ReconVault v1.0.0 - Cyber Intelligence Platform');
          break;
        default:
          console.log('Unknown menu action:', action);
      }
    },
    [success]
  );

  // Search handlers
  const handleSearch = useCallback(
    (query) => {
      success(`Searching for: ${query}`);
      updateFilters({ searchQuery: query });
    },
    [success, updateFilters]
  );

  // Animation variants
  const layoutVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-cyber-black text-neon-green font-mono overflow-x-hidden overflow-y-auto">
        {/* Background Effects */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-cyber-dark via-cyber-black to-cyber-darker"></div>
          <div
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300ff41' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}
          ></div>
        </div>

        {/* Main Layout */}
        <motion.div
          variants={layoutVariants}
          initial="hidden"
          animate="visible"
          className="min-h-screen flex flex-col"
        >
          {/* Top Header */}
          <TopHeader
            onSearch={handleSearch}
            onFilterToggle={() => setShowAdvancedFilters(!showAdvancedFilters)}
            onMenuAction={handleMenuAction}
            systemStatus={systemStatus}
            showAdvancedFilters={showAdvancedFilters}
            onAdvancedFiltersToggle={() => setShowAdvancedFilters(!showAdvancedFilters)}
          />

          {/* Backend Connection Banner */}
          <ConnectionError
            show={!backendState.connected}
            apiBaseUrl={apiBaseUrl}
            wsUrl={wsUrl}
            lastError={backendState.lastError}
            checking={backendState.checking}
            nextRetryInMs={nextRetryInMs}
            onRetry={() => checkBackend(true)}
          />

          {/* Main Content Area */}
          <div className="flex-1 flex min-h-0 overflow-hidden">
            <LeftSidebar
              isCollapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
              activeTab="search"
              collectionHistory={collectionHistory}
              activeTasks={activeTasks}
              onStartCollection={handleStartCollection}
            />

            <div className="flex-1 relative min-h-0" ref={graphContainerRef}>
              {activeView === 'graph' ? (
                <GraphCanvas
                  nodes={graphData.nodes}
                  edges={graphData.edges}
                  selectedNode={selectedNode}
                  selectedEdge={selectedEdge}
                  onNodeSelect={handleNodeSelect}
                  onNodeHover={handleNodeHover}
                  onEdgeSelect={handleEdgeSelect}
                  onEdgeHover={handleEdgeHover}
                  filters={filters}
                  width={graphContainerSize.width}
                  height={graphContainerSize.height}
                  className="w-full h-full"
                />
              ) : (
                <ComplianceDashboard />
              )}

              {/* Loading Overlay */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 bg-cyber-black bg-opacity-80 flex items-center justify-center z-50"
                >
                  <div className="text-center">
                    <div className="loading-spinner mb-4" />
                    <p className="text-neon-green font-mono">Loading graph data...</p>
                  </div>
                </motion.div>
              )}

              {/* Non-network errors */}
              {error && backendState.connected && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 bg-danger-red bg-opacity-80 flex items-center justify-center z-50"
                >
                  <div className="text-center max-w-lg px-6">
                    <div className="text-4xl mb-4">⚠️</div>
                    <p className="text-white font-mono break-words">Error: {error}</p>
                    <button
                      onClick={refreshGraph}
                      className="mt-4 px-4 py-2 bg-white text-danger-red rounded font-mono hover:bg-gray-100"
                    >
                      Retry
                    </button>
                  </div>
                </motion.div>
              )}

              {usingDemoData && (
                <div className="absolute top-3 left-3 bg-cyber-dark/80 border border-warning-yellow/40 text-warning-yellow px-3 py-2 rounded-lg text-xs font-mono">
                  Demo mode: backend offline
                </div>
              )}
            </div>

            <RightSidebar
              selectedNode={selectedNode}
              selectedEdge={selectedEdge}
              isCollapsed={rightSidebarCollapsed}
              onToggleCollapse={() => setRightSidebarCollapsed(!rightSidebarCollapsed)}
              onEntityAction={handleEntityAction}
              onRelationshipAction={handleRelationshipAction}
            />
          </div>

          {/* Bottom Stats */}
          <BottomStats
            toast={toast}
            isCollapsed={bottomStatsCollapsed}
            onToggleCollapse={() => setBottomStatsCollapsed(!bottomStatsCollapsed)}
            nodes={graphData.nodes}
            edges={graphData.edges}
            performance={performance}
          />
        </motion.div>

        <SettingsPanel
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          onSettingsChange={() => success('Settings saved')}
        />

        <ToastContainer position="top-right" />

        {/* Background Animation Elements */}
        <div className="fixed inset-0 pointer-events-none -z-20">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
            className="absolute top-20 left-20 w-2 h-2 bg-neon-green rounded-full"
          />
          <motion.div
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.2, 0.5, 0.2]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 1
            }}
            className="absolute top-40 right-32 w-1 h-1 bg-neon-cyan rounded-full"
          />
          <motion.div
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.4, 0.7, 0.4]
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 2
            }}
            className="absolute bottom-32 left-40 w-1.5 h-1.5 bg-neon-purple rounded-full"
          />
          <motion.div
            animate={{
              scale: [1, 1.4, 1],
              opacity: [0.3, 0.6, 0.3]
            }}
            transition={{
              duration: 3.5,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.5
            }}
            className="absolute bottom-20 right-20 w-2 h-2 bg-neon-magenta rounded-full"
          />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
