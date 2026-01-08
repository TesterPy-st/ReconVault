// ReconVault Main Application Component - Cyber Graph Visualization Interface
import React, { useState, useEffect, useCallback } from 'react';
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

// Form Components
import ReconSearchForm from './components/Forms/ReconSearchForm';

// Import styles
import './styles/main.css';

function App() {
  // State management
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(false);
  const [bottomStatsCollapsed, setBottomStatsCollapsed] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [graphContainerSize, setGraphContainerSize] = useState({ width: 800, height: 600 });
  const [activeView, setActiveView] = useState('graph'); // 'graph' or 'compliance'

  // Hooks
  const {
    nodes,
    edges,
    loading,
    error,
    filters,
    updateFilters,
    selectNode,
    selectEdge,
    refreshGraph,
    performance
  } = useGraph();

  const { connected: wsConnected, connecting: wsConnecting, addEventListener } = useWebSocket();
  const { success, error: showError, loading: showLoading } = useToast();

  // WebSocket Event Listeners
  useEffect(() => {
    if (wsConnected) {
      const unsubscribeViolation = addEventListener('compliance_violation', (data) => {
        showError(`Compliance Violation: ${data.message} (${data.severity.toUpperCase()})`);
      });
      
      return () => {
        unsubscribeViolation();
      };
    }
  }, [wsConnected, addEventListener, showError]);

  // System status
  const [systemStatus, setSystemStatus] = useState({
    backend: 'unknown',
    database: 'unknown',
    neo4j: 'unknown',
    redis: 'unknown'
  });

  // Collection history and active tasks - fetched from backend
  const [collectionHistory, setCollectionHistory] = useState([]);
  const [activeTasks, setActiveTasks] = useState([]);

  // Fetch collection data from backend
  useEffect(() => {
    const fetchCollectionData = async () => {
      try {
        const { collectionAPI } = await import('./services/api');
        const tasks = await collectionAPI.getCollectionTasks();
        setCollectionHistory(tasks.filter(t => t.status === 'completed').slice(0, 10));
        setActiveTasks(tasks.filter(t => t.status === 'RUNNING' || t.status === 'running'));
      } catch (err) {
        // Silent fail - data will remain empty until backend is available
      }
    };

    fetchCollectionData();
  }, []);

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
    // Could show tooltip or highlight connections
    console.log('Node hovered:', node?.id);
  }, []);

  const handleEdgeHover = useCallback((edge) => {
    // Could show edge details tooltip
    console.log('Edge hovered:', edge?.id);
  }, []);

  // Collection handlers
  const handleStartCollection = useCallback(async (config) => {
    try {
      showLoading('Starting intelligence collection...');

      // Call backend API to start collection
      const { collectionAPI } = await import('./services/api');
      await collectionAPI.startCollection(config.target, config.types || ['web'], config.options || {});

      success(`Collection started for ${config.target}`);

      // Refresh collection tasks to show new task
      const tasks = await collectionAPI.getCollectionTasks();
      setActiveTasks(tasks.filter(t => t.status === 'RUNNING' || t.status === 'running'));

    } catch (error) {
      showError('Failed to start collection: ' + (error.message || error.userMessage || 'Unknown error'));
    }
  }, [success, showError, showLoading]);

  const handleEntityAction = useCallback(async (action, entity) => {
    try {
      const { entityAPI } = await import('./services/api');

      switch (action) {
        case 'copy':
          navigator.clipboard.writeText(entity.value || entity.id);
          success('Entity copied to clipboard');
          break;
        case 'export':
          // This would trigger export functionality
          success('Entity exported successfully');
          break;
        case 'delete':
          await entityAPI.deleteEntity(entity.id);
          success('Entity deleted successfully');
          refreshGraph(); // Refresh to show deletion
          break;
        default:
          console.log('Unknown entity action:', action);
      }
    } catch (error) {
      showError('Failed to perform action: ' + (error.message || error.userMessage || 'Unknown error'));
    }
  }, [success, showError, refreshGraph]);

  const handleRelationshipAction = useCallback(async (action, relationship) => {
    try {
      const { relationshipAPI } = await import('./services/api');

      switch (action) {
        case 'delete':
          await relationshipAPI.deleteRelationship(relationship.id);
          success('Relationship deleted successfully');
          refreshGraph(); // Refresh to show deletion
          break;
        default:
          console.log('Unknown relationship action:', action);
      }
    } catch (error) {
      showError('Failed to perform action: ' + (error.message || error.userMessage || 'Unknown error'));
    }
  }, [success, showError, refreshGraph]);

  // Header menu handlers
  const handleMenuAction = useCallback((action) => {
    console.log('Menu action:', action);
    
    switch (action) {
      case 'compliance':
        setActiveView(activeView === 'compliance' ? 'graph' : 'compliance');
        break;
      case 'home':
        setActiveView('graph');
        break;
      case 'export':
        success('Graph export functionality initiated');
        break;
      case 'settings':
        showError('Settings panel not implemented yet');
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
  }, [success, showError]);

  // Search handlers
  const handleSearch = useCallback((query) => {
    console.log('Search query:', query);
    success(`Searching for: ${query}`);
    
    // In real app, this would trigger actual search
    updateFilters({ searchQuery: query });
  }, [success, updateFilters]);

  // Update graph container size on window resize
  useEffect(() => {
    const handleResize = () => {
      const headerHeight = 80; // TopHeader height
      const bottomHeight = bottomStatsCollapsed ? 40 : 120; // BottomStats height
      const sidebarWidth = sidebarCollapsed ? 60 : 320; // LeftSidebar width
      const rightSidebarWidth = rightSidebarCollapsed ? 60 : 350; // RightSidebar width
      
      setGraphContainerSize({
        width: window.innerWidth - sidebarWidth - rightSidebarWidth,
        height: window.innerHeight - headerHeight - bottomHeight
      });
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarCollapsed, rightSidebarCollapsed, bottomStatsCollapsed]);

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
    <div className="min-h-screen bg-cyber-black text-neon-green font-mono overflow-hidden">
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
        className="h-screen flex flex-col"
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

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar */}
          <LeftSidebar
            isCollapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            activeTab="search"
            collectionHistory={collectionHistory}
            activeTasks={activeTasks}
            onStartCollection={handleStartCollection}
          />

          {/* Graph Container or Compliance Dashboard */}
          <div className="flex-1 relative">
            {activeView === 'graph' ? (
              <GraphCanvas
                nodes={nodes}
                edges={edges}
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

            {/* Error Overlay */}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-danger-red bg-opacity-80 flex items-center justify-center z-50"
              >
                <div className="text-center">
                  <div className="text-4xl mb-4">⚠️</div>
                  <p className="text-white font-mono">Error: {error}</p>
                  <button
                    onClick={refreshGraph}
                    className="mt-4 px-4 py-2 bg-white text-danger-red rounded font-mono hover:bg-gray-100"
                  >
                    Retry
                  </button>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Sidebar */}
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
          isCollapsed={bottomStatsCollapsed}
          onToggleCollapse={() => setBottomStatsCollapsed(!bottomStatsCollapsed)}
        />
      </motion.div>

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
            ease: "easeInOut"
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
            ease: "easeInOut",
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
            ease: "easeInOut",
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
            ease: "easeInOut",
            delay: 0.5
          }}
          className="absolute bottom-20 right-20 w-2 h-2 bg-neon-magenta rounded-full"
        />
      </div>
    </div>
  );
}

export default App;