// ReconVault Main Application with Routing

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './components/ui/Toast';
import uiStore from './stores/uiStore';

// Pages
import Dashboard from './pages/Dashboard';
import GraphPage from './pages/Graph';
import IntelligencePage from './pages/Intelligence';
import SettingsPage from './pages/Settings';
import AboutPage from './pages/About';
import TargetDetailPage from './pages/TargetDetail';

// Context/Providers wrapper
const AppProviders = ({ children }) => {
  return <ToastProvider>{children}</ToastProvider>;
};

// Scroll to top on route change
const ScrollToTop = () => {
  const { pathname } = window.location;
  
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  
  return null;
};

// Main App Component
function App() {
  const { theme } = uiStore();
  
  return (
    <BrowserRouter>
      <ScrollToTop />
      <AppProviders>
        <div className={`min-h-screen bg-cyber-dark ${theme}`}>
          <Routes>
            {/* Dashboard - Home */}
            <Route path="/" element={<Dashboard />} />
            
            {/* Graph Explorer */}
            <Route path="/graph" element={<GraphPage />} />
            
            {/* Intelligence */}
            <Route path="/intelligence" element={<IntelligencePage />} />
            
            {/* Settings */}
            <Route path="/settings" element={<SettingsPage />} />
            
            {/* About */}
            <Route path="/about" element={<AboutPage />} />
            
            {/* Target Details */}
            <Route path="/target/:id" element={<TargetDetailPage />} />
            
            {/* Legacy routes */}
            <Route path="/targets" element={<Navigate to="/" replace />} />
            <Route path="/entities" element={<Navigate to="/intelligence" replace />} />
            <Route path="/analytics" element={<Navigate to="/" replace />} />
            
            {/* 404 - Not Found */}
            <Route
              path="*"
              element={
                <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-6xl font-bold text-neon-green font-cyber mb-4">404</h1>
                    <p className="text-xl text-cyber-gray mb-6">Page Not Found</p>
                    <a
                      href="/"
                      className="inline-flex items-center gap-2 px-6 py-3 bg-neon-green text-cyber-dark rounded-lg font-bold hover:bg-opacity-80 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                      </svg>
                      Back to Dashboard
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </div>
      </AppProviders>
    </BrowserRouter>
  );
}

export default App;
