// ReconVault Sidebar Component

import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import uiStore from '../../stores/uiStore';
import targetStore from '../../stores/targetStore';

const Sidebar = () => {
  const location = useLocation();
  const {
    sidebarOpen,
    sidebarCollapsed,
    sidebarMobileOpen,
    setSidebarMobileOpen,
  } = uiStore();
  
  const { stats } = targetStore();
  
  const menuItems = [
    {
      section: 'Main',
      items: [
        { path: '/', label: 'Dashboard', icon: 'dashboard' },
        { path: '/graph', label: 'Graph Explorer', icon: 'graph' },
        { path: '/intelligence', label: 'Intelligence', icon: 'intelligence' },
      ],
    },
    {
      section: 'Management',
      items: [
        { path: '/targets', label: 'Targets', icon: 'target', badge: stats.total },
        { path: '/entities', label: 'Entities', icon: 'entity' },
        { path: '/analytics', label: 'Analytics', icon: 'analytics' },
      ],
    },
    {
      section: 'System',
      items: [
        { path: '/settings', label: 'Settings', icon: 'settings' },
        { path: '/about', label: 'About', icon: 'about' },
      ],
    },
  ];
  
  const getIcon = (icon) => {
    const icons = {
      dashboard: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      ),
      graph: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
      intelligence: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      target: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      entity: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      analytics: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      settings: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      about: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    };
    return icons[icon] || null;
  };
  
  // Mobile overlay
  const MobileOverlay = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 z-30 lg:hidden"
      onClick={() => setSidebarMobileOpen(false)}
    />
  );
  
  // Sidebar content
  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-4 border-b border-cyber-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-green to-neon-blue flex items-center justify-center flex-shrink-0">
            <span className="text-cyber-dark font-bold font-cyber">RV</span>
          </div>
          {!sidebarCollapsed && (
            <div>
              <h1 className="text-lg font-bold font-cyber text-neon-green">RECONVAULT</h1>
              <p className="text-xs text-cyber-gray">Cyber Intelligence</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Quick stats */}
      <div className="p-4 border-b border-cyber-border">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-cyber-darker rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-neon-green">{stats.total || 0}</p>
            <p className="text-xs text-cyber-gray">Targets</p>
          </div>
          <div className="bg-cyber-darker rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-neon-blue">{stats.completed || 0}</p>
            <p className="text-xs text-cyber-gray">Completed</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((section) => (
          <div key={section.section} className="mb-4">
            {!sidebarCollapsed && (
              <h3 className="px-4 mb-2 text-xs font-semibold text-cyber-gray uppercase tracking-wider">
                {section.section}
              </h3>
            )}
            <ul className="space-y-1 px-2">
              {section.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-neon-green/20 text-neon-green'
                          : 'text-cyber-gray hover:text-neon-green hover:bg-cyber-light'
                      }`
                    }
                  >
                    {getIcon(item.icon)}
                    {!sidebarCollapsed && (
                      <>
                        <span className="flex-1 text-sm font-medium">{item.label}</span>
                        {item.badge !== undefined && (
                          <span className="px-2 py-0.5 rounded-full bg-neon-green/20 text-neon-green text-xs">
                            {item.badge}
                          </span>
                        )}
                      </>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
      
      {/* Bottom section */}
      <div className="p-4 border-t border-cyber-border">
        {!sidebarCollapsed ? (
          <div className="bg-cyber-darker rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-cyber-gray">System Online</span>
            </div>
            <p className="text-xs text-cyber-gray">
              Last sync: {new Date().toLocaleTimeString()}
            </p>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
  
  return (
    <>
      {/* Mobile overlay */}
      {sidebarMobileOpen && <MobileOverlay />}
      
      {/* Sidebar */}
      <motion.aside
        className={`
          fixed left-0 top-16 bottom-0 z-30
          bg-cyber-light border-r border-cyber-border
          transition-all duration-300
          ${sidebarMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarCollapsed ? 'w-20' : 'w-64'}
        `}
        initial={false}
        animate={{
          width: sidebarCollapsed ? 80 : 256,
        }}
      >
        <SidebarContent />
      </motion.aside>
    </>
  );
};

export default Sidebar;
