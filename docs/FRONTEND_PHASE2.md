# Phase 2: Advanced Graph Analytics & Real-Time UI Features

## Overview
This phase implements advanced graph analytics, intelligent filtering, sophisticated search capabilities, and comprehensive UI enhancements for the ReconVault intelligence platform.

## New Services

### 1. Graph Analytics Service (`src/services/graphAnalytics.js`)
Advanced graph analysis and community detection algorithms.

**Features:**
- **Metrics Calculation**: Node centrality (betweenness, closeness, degree), clustering coefficient, graph diameter, average shortest path
- **Community Detection**: Louvain-like algorithm for grouping related entities
- **Pathfinding**: Shortest paths and all paths between nodes
- **Anomaly Detection**: Identifies isolated nodes, bridge nodes, hubs, and suspicious patterns
- **Node Influence**: Calculates propagation impact scores
- **Connection Suggestions**: ML-based entity similarity matching

**Usage:**
```javascript
import graphAnalytics from './services/graphAnalytics';

// Calculate comprehensive metrics
const metrics = graphAnalytics.calculateGraphMetrics(nodes, edges);

// Detect communities
const communities = graphAnalytics.detectCommunities(nodes, edges);

// Find paths
const paths = graphAnalytics.findPathsBetween(sourceId, targetId, nodes, edges);

// Detect anomalies
const anomalies = graphAnalytics.detectAnomalies(nodes, edges);

// Calculate influence
const influence = graphAnalytics.calculateNodeInfluence(node, edges);

// Get suggestions
const suggestions = graphAnalytics.suggestConnections(node, allNodes);
```

### 2. Export Service (`src/services/exportService.js`)
Multi-format graph export functionality.

**Supported Formats:**
- **JSON**: Full graph data with metadata
- **CSV**: Separate files for nodes and edges
- **PNG**: Screenshot with watermark
- **SVG**: Vector format for editing
- **Neo4j Cypher**: Import format for Neo4j
- **GML**: Graph Modelling Language
- **GraphML**: XML-based graph format

**Usage:**
```javascript
import exportService from './services/exportService';

// Export as JSON
exportService.exportJSON(data, 'graph-export.json');

// Export as CSV
exportService.exportCSV(data, 'graph-export');

// Export as image
await exportService.exportImage(canvas, 'png', 'graph-export');

// Export for Neo4j
exportService.exportNeo4j(data, 'graph-export.cypher');

// Create shareable link
const shareUrl = exportService.shareGraphLink(data);
```

### 3. Snapshot Service (`src/services/snapshotService.js`)
Graph state management with IndexedDB storage.

**Features:**
- Capture and restore graph states
- Compare snapshots to see changes
- Import/export snapshots
- Automatic cleanup of old snapshots

**Usage:**
```javascript
import snapshotService from './services/snapshotService';

// Capture snapshot
const snapshot = await snapshotService.captureSnapshot(graphData, 'My Snapshot');

// List snapshots
const snapshots = await snapshotService.listSnapshots();

// Load snapshot
const data = await snapshotService.loadSnapshot(snapshotId);

// Compare snapshots
const comparison = await snapshotService.compareSnapshots(id1, id2);

// Delete snapshot
await snapshotService.deleteSnapshot(snapshotId);
```

### 4. Playlist Service (`src/services/playlistService.js`)
Entity collections and bookmarks management.

**Features:**
- Create named playlists/collections
- Add/remove entities from collections
- Bookmark interesting entities
- Export and share collections

**Usage:**
```javascript
import playlistService from './services/playlistService';

// Create playlist
const playlist = await playlistService.createPlaylist('Investigation 1', 'Malware campaign');

// Add entity to playlist
await playlistService.addToPlaylist(playlistId, entityId, entityData);

// Get all playlists
const playlists = await playlistService.getAllPlaylists();

// Bookmark entity
await playlistService.addBookmark(entityId, entityData);

// Check if bookmarked
const isBookmarked = await playlistService.isBookmarked(entityId);

// Toggle bookmark
await playlistService.toggleBookmark(entityId, entityData);
```

### 5. Performance Service (`src/services/performanceService.js`)
Real-time performance monitoring and metrics.

**Features:**
- FPS monitoring
- Render time tracking
- API latency measurement
- WebSocket latency tracking
- Memory usage monitoring
- Performance recommendations

**Usage:**
```javascript
import performanceService from './services/performanceService';

// Start monitoring
performanceService.startMonitoring();

// Get current metrics
const metrics = performanceService.getCurrentMetrics();

// Measure async operation
const result = await performanceService.measureAsync('apiCall', async () => {
  return await fetchData();
}, 'api');

// Get performance report
const report = performanceService.getPerformanceReport();

// Export metrics
performanceService.exportMetrics();
```

## New Components

### 1. Error Boundary (`src/components/Common/ErrorBoundary.jsx`)
React error boundary for graceful error handling.

**Features:**
- Catches component errors
- Shows detailed error info in development
- User-friendly message in production
- Recovery options (retry, reload, go home)
- Error logging support

**Usage:**
```jsx
import ErrorBoundary from './components/Common/ErrorBoundary';

<ErrorBoundary>
  <YourApp />
</ErrorBoundary>
```

### 2. Theme Switcher (`src/components/Common/ThemeSwitcher.jsx`)
Dynamic theme selection component.

**Available Themes:**
- **Cyber Dark**: Neon green on dark (default)
- **Neon Magenta**: Pink and magenta focus
- **Hacker Green**: Classic Matrix green
- **Synthwave**: 80s pink and purple
- **Minimal**: Subtle colors

**Features:**
- System theme detection
- Theme persistence
- Smooth transitions
- Color preview

**Usage:**
```jsx
import ThemeSwitcher from './components/Common/ThemeSwitcher';

<ThemeSwitcher className="ml-4" />
```

### 3. Help Panel (`src/components/Common/HelpPanel.jsx`)
Interactive help and documentation panel.

**Features:**
- Keyboard shortcuts reference
- Feature documentation
- Search functionality
- About information
- Quick tips

**Usage:**
```jsx
import HelpPanel from './components/Common/HelpPanel';

const [helpOpen, setHelpOpen] = useState(false);

<HelpPanel isOpen={helpOpen} onClose={() => setHelpOpen(false)} />
```

### 4. Settings Panel (`src/components/Common/SettingsPanel.jsx`)
Comprehensive settings management.

**Settings Categories:**
- **Graph**: Simulation speed, labels, glow, animations, performance mode
- **Notifications**: Duration, position, sound, type filters
- **API**: Backend URL, WebSocket URL, timeout, retry
- **Export**: Default format, metadata inclusion, watermark

**Usage:**
```jsx
import SettingsPanel from './components/Common/SettingsPanel';

<SettingsPanel 
  isOpen={settingsOpen} 
  onClose={() => setSettingsOpen(false)}
  onSettingsChange={(settings) => console.log(settings)}
/>
```

### 5. Advanced Search (`src/components/Forms/AdvancedSearch.jsx`)
Powerful search with query syntax support.

**Search Modes:**
- **Simple**: Text-based search with fuzzy matching
- **Advanced**: Multi-field queries with operators

**Query Syntax:**
```
type:DOMAIN source:web value:*.example.com
riskLevel:HIGH confidence:[0.8 TO 1.0]
/regex-pattern/ for pattern matching
AND, OR, NOT operators
[2024-01-01 TO 2024-12-31] date ranges
```

**Features:**
- Search history
- Auto-suggestions
- Result highlighting
- Save searches

**Usage:**
```jsx
import AdvancedSearch from './components/Forms/AdvancedSearch';

<AdvancedSearch 
  isOpen={searchOpen}
  onClose={() => setSearchOpen(false)}
  onSearch={handleSearch}
/>
```

## Keyboard Shortcuts

### Navigation
- `C` - Center view
- `F` - Fit to screen
- `+` / `-` - Zoom in/out
- `Arrow Keys` - Pan view
- `Ctrl+A` - Select all nodes
- `Escape` - Deselect all

### Search & Filter
- `Ctrl+F` - Focus search
- `Ctrl+Shift+F` - Advanced search
- `Ctrl+K` - Filter menu
- `/` - Quick search

### Export & Save
- `Ctrl+E` - Export graph
- `Ctrl+S` - Save snapshot
- `Ctrl+L` - Share/copy link

### Help
- `?` - Keyboard shortcuts
- `H` - Help panel

### Other
- `Delete` - Delete selected nodes
- `Space` - Toggle simulation pause
- `Ctrl+Shift+D` - Toggle debug overlay

## Custom Hooks

### useKeyboardShortcuts
Custom hook for managing keyboard shortcuts.

**Usage:**
```javascript
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts';

const shortcuts = {
  'c': () => centerView(),
  'f': () => fitToScreen(),
  'ctrl+f': () => focusSearch(),
  'delete': () => deleteSelected()
};

useKeyboardShortcuts(shortcuts, enabled);
```

## Data Persistence

All user data is stored locally using IndexedDB and localStorage:

**IndexedDB Stores:**
- `snapshots` - Graph state snapshots
- `playlists` - Entity collections
- `bookmarks` - Bookmarked entities

**LocalStorage Keys:**
- `reconvault_theme` - Selected theme
- `reconvault_system_theme` - System theme preference
- `reconvault_settings` - User settings
- `reconvault_search_history` - Recent searches
- `reconvault_playlists` - Playlist data (fallback)
- `reconvault_bookmarks` - Bookmark data (fallback)

## Performance Optimization

### Implemented Optimizations:
1. **Caching**: Analytics results cached for reuse
2. **Debouncing**: Search and filter inputs debounced
3. **Virtual Scrolling**: Long lists use virtual scrolling
4. **Lazy Loading**: Components loaded on demand
5. **Code Splitting**: Dynamic imports for route-based splitting
6. **IndexedDB**: Large data stored in IndexedDB, not memory
7. **Performance Modes**: Adjustable quality settings

### Performance Targets:
- **FPS**: >60 FPS on modern devices
- **Render Time**: <16ms per frame
- **API Latency**: <500ms average
- **Memory**: <500MB for typical graphs

## Testing

Tests should be created for:
- All service methods
- Component rendering
- User interactions
- Data transformations
- Error scenarios
- Performance edge cases

**Example Test Structure:**
```javascript
// src/__tests__/graphAnalytics.test.js
import graphAnalytics from '../services/graphAnalytics';

describe('GraphAnalytics', () => {
  test('calculates graph metrics correctly', () => {
    const metrics = graphAnalytics.calculateGraphMetrics(nodes, edges);
    expect(metrics.nodeCount).toBe(5);
    expect(metrics.density).toBeGreaterThan(0);
  });
  
  test('detects communities', () => {
    const communities = graphAnalytics.detectCommunities(nodes, edges);
    expect(communities.length).toBeGreaterThan(0);
  });
});
```

## Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Dependencies

### New Dependencies:
None - all functionality implemented with existing dependencies (React, Framer Motion, D3.js)

### Required Browser APIs:
- IndexedDB (for snapshots and playlists)
- localStorage (for settings)
- Clipboard API (for copy functionality)
- Performance API (for monitoring)

## Migration Guide

### From Phase 1:
1. Import new services where needed
2. Wrap app in ErrorBoundary
3. Add keyboard shortcuts hook to main app
4. Add theme switcher to header
5. Add help and settings buttons to UI
6. Replace simple search with AdvancedSearch component

### Example Integration:
```jsx
import ErrorBoundary from './components/Common/ErrorBoundary';
import ThemeSwitcher from './components/Common/ThemeSwitcher';
import HelpPanel from './components/Common/HelpPanel';
import SettingsPanel from './components/Common/SettingsPanel';
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts';

function App() {
  const [helpOpen, setHelpOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  
  const shortcuts = {
    '?': () => setHelpOpen(true),
    'h': () => setHelpOpen(true),
    'ctrl+,': () => setSettingsOpen(true)
  };
  
  useKeyboardShortcuts(shortcuts);
  
  return (
    <ErrorBoundary>
      <div className="app">
        <Header>
          <ThemeSwitcher />
          <button onClick={() => setHelpOpen(true)}>Help</button>
          <button onClick={() => setSettingsOpen(true)}>Settings</button>
        </Header>
        
        <MainContent />
        
        <HelpPanel isOpen={helpOpen} onClose={() => setHelpOpen(false)} />
        <SettingsPanel isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
      </div>
    </ErrorBoundary>
  );
}
```

## Future Enhancements

Potential improvements for Phase 3:
- AI-powered entity classification
- Automated threat scoring
- Real-time collaborative editing
- Advanced visualization modes (3D, VR)
- Integration with external threat intelligence feeds
- Custom plugin system
- Mobile app
- Offline mode with service workers

## License

Copyright © 2024 ReconVault. All rights reserved.
