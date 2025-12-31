// ReconVault Layout Component

import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import uiStore from '../../stores/uiStore';

const Layout = () => {
  const { sidebarCollapsed, sidebarMobileOpen } = uiStore();
  
  return (
    <div className="min-h-screen bg-cyber-dark">
      {/* Background effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyber-darker via-cyber-dark to-cyber-darker" />
        <div className="absolute top-0 left-0 w-full h-full opacity-5">
          <div className="absolute top-10 left-10 w-96 h-96 bg-neon-green/20 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-neon-blue/20 rounded-full blur-3xl" />
        </div>
      </div>
      
      {/* Header */}
      <Header />
      
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main content area */}
      <div
        className={`
          transition-all duration-300
          pt-16
          ${sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'}
        `}
      >
        {/* Mobile sidebar open state */}
        {sidebarMobileOpen && (
          <div className="fixed inset-0 bg-black/50 z-30 lg:hidden" />
        )}
        
        {/* Page content */}
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
