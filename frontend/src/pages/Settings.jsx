// ReconVault Settings Page

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import uiStore from '../stores/uiStore';
import targetStore from '../stores/targetStore';

const SettingsPage = () => {
  const { settings, updateSettings, theme, setTheme } = uiStore();
  const { stats, fetchStats } = targetStore();
  
  const [activeTab, setActiveTab] = useState('general');
  
  const tabs = [
    { id: 'general', label: 'General' },
    { id: 'notifications', label: 'Notifications' },
    { id: 'appearance', label: 'Appearance' },
    { id: 'data', label: 'Data & Storage' },
    { id: 'api', label: 'API Keys' },
    { id: 'about', label: 'About' },
  ];
  
  const handleSave = () => {
    console.log('Settings saved');
  };
  
  const handleReset = () => {
    uiStore.getState().resetSettings();
  };
  
  const handleClearCache = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.reload();
  };
  
  return (
    <Layout>
      <MainContent>
        <div className="max-w-4xl mx-auto">
          {/* Page header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-neon-green font-cyber">
              Settings
            </h1>
            <p className="text-cyber-gray">
              Configure your ReconVault preferences
            </p>
          </div>
          
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar */}
            <div className="lg:w-64">
              <nav className="bg-cyber-light rounded-lg border border-cyber-border p-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full text-left px-4 py-2.5 rounded-lg text-sm transition-colors
                      ${
                        activeTab === tab.id
                          ? 'bg-neon-green/20 text-neon-green'
                          : 'text-cyber-gray hover:text-neon-green hover:bg-cyber-darker'
                      }
                    `}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>
            
            {/* Content */}
            <div className="flex-1">
              {activeTab === 'general' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">General Settings</h2>
                  
                  <div className="space-y-4">
                    <Input
                      label="Application Name"
                      value="ReconVault"
                      disabled
                      hint="The name displayed in the header"
                    />
                    
                    <Select
                      label="Default Target Type"
                      value={settings.defaultTargetType || 'domain'}
                      onChange={(value) => updateSettings({ defaultTargetType: value })}
                      options={[
                        { value: 'domain', label: 'Domain' },
                        { value: 'ip_address', label: 'IP Address' },
                        { value: 'email', label: 'Email' },
                        { value: 'phone', label: 'Phone' },
                      ]}
                    />
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Auto Refresh</h3>
                        <p className="text-sm text-cyber-gray">Automatically refresh data at intervals</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ autoRefresh: !settings.autoRefresh })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.autoRefresh ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.autoRefresh ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    {settings.autoRefresh && (
                      <Select
                        label="Refresh Interval"
                        value={settings.refreshInterval || 30000}
                        onChange={(value) => updateSettings({ refreshInterval: parseInt(value) })}
                        options={[
                          { value: 10000, label: '10 seconds' },
                          { value: 30000, label: '30 seconds' },
                          { value: 60000, label: '1 minute' },
                          { value: 300000, label: '5 minutes' },
                        ]}
                      />
                    )}
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'notifications' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">Notification Settings</h2>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Enable Notifications</h3>
                        <p className="text-sm text-cyber-gray">Receive browser notifications</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ notifications: !settings.notifications })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.notifications ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.notifications ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Sound Effects</h3>
                        <p className="text-sm text-cyber-gray">Play sounds for notifications</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ sound: !settings.sound })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.sound ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.sound ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Risk Alerts</h3>
                        <p className="text-sm text-cyber-gray">Notify when high-risk entities are found</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ riskAlerts: !settings.riskAlerts })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.riskAlerts ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.riskAlerts ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'appearance' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">Appearance</h2>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Dark Mode</h3>
                        <p className="text-sm text-cyber-gray">Use dark theme (always on)</p>
                      </div>
                      <button
                        onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          theme === 'dark' ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            theme === 'dark' ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Show Risk Colors</h3>
                        <p className="text-sm text-cyber-gray">Color-code entities by risk level</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ showRiskColors: !settings.showRiskColors })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.showRiskColors ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.showRiskColors ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Show Labels</h3>
                        <p className="text-sm text-cyber-gray">Display node labels on graph</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ showLabels: !settings.showLabels })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.showLabels ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.showLabels ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Animations</h3>
                        <p className="text-sm text-cyber-gray">Enable UI animations</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ animations: !settings.animations })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.animations ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.animations ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-cyber-darker rounded-lg">
                      <div>
                        <h3 className="font-medium text-neon-green">Compact Mode</h3>
                        <p className="text-sm text-cyber-gray">Use compact UI layout</p>
                      </div>
                      <button
                        onClick={() => updateSettings({ compactMode: !settings.compactMode })}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.compactMode ? 'bg-neon-green' : 'bg-cyber-border'
                        }`}
                      >
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${
                            settings.compactMode ? 'translate-x-6' : 'translate-x-0.5'
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'data' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">Data & Storage</h2>
                  
                  <div className="space-y-4">
                    <div className="p-4 bg-cyber-darker rounded-lg">
                      <h3 className="font-medium text-neon-green mb-2">Storage Usage</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-cyber-gray">Local Storage</span>
                          <span className="text-neon-green font-mono">~0 KB</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-cyber-gray">Session Storage</span>
                          <span className="text-neon-green font-mono">~0 KB</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-cyber-gray">IndexedDB</span>
                          <span className="text-neon-green font-mono">~0 KB</span>
                        </div>
                      </div>
                    </div>
                    
                    <Button variant="outline" className="w-full" onClick={handleClearCache}>
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Clear Cache
                    </Button>
                    
                    <Button variant="outline" className="w-full">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Export Settings
                    </Button>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'api' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">API Configuration</h2>
                  
                  <div className="space-y-4">
                    <Input
                      label="Backend API URL"
                      value="/api"
                      disabled
                      hint="Currently connected to local backend"
                    />
                    
                    <Input
                      label="WebSocket URL"
                      value="ws://localhost:8000/ws"
                      disabled
                    />
                    
                    <div className="p-4 bg-neon-green/10 border border-neon-green/30 rounded-lg">
                      <p className="text-sm text-neon-green">
                        Connected to backend. All API calls are proxied through Vite dev server.
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}
              
              {activeTab === 'about' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 space-y-6"
                >
                  <h2 className="text-lg font-semibold text-neon-green">About ReconVault</h2>
                  
                  <div className="text-center py-4">
                    <div className="w-20 h-20 mx-auto rounded-xl bg-gradient-to-br from-neon-green to-neon-blue flex items-center justify-center mb-4">
                      <span className="text-cyber-dark font-bold font-cyber text-2xl">RV</span>
                    </div>
                    <h3 className="text-xl font-bold text-neon-green">ReconVault v0.1.0</h3>
                    <p className="text-cyber-gray mt-2">
                      Cyber Reconnaissance Intelligence System
                    </p>
                  </div>
                  
                  <div className="p-4 bg-cyber-darker rounded-lg">
                    <h4 className="font-medium text-neon-green mb-3">Development Team</h4>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <span className="text-neon-blue">•</span>
                        <span>Simanchala Bisoyi - Lead Architect & Backend Developer</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="text-neon-blue">•</span>
                        <span>Subham Mohanty - Frontend Specialist & UI/UX Designer</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="text-neon-blue">•</span>
                        <span>Abhinav Kumar - DevOps & Infrastructure Engineer</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-cyber-darker rounded-lg text-center">
                      <p className="text-2xl font-bold text-neon-green font-mono">{stats.total || 0}</p>
                      <p className="text-sm text-cyber-gray">Total Targets</p>
                    </div>
                    <div className="p-4 bg-cyber-darker rounded-lg text-center">
                      <p className="text-2xl font-bold text-neon-blue font-mono">Active</p>
                      <p className="text-sm text-cyber-gray">System Status</p>
                    </div>
                  </div>
                  
                  <div className-sm text-cyber="text-center text-gray">
                    <p>Built with React, FastAPI, PostgreSQL, Neo4j, and Docker</p>
                    <p className="mt-1">© 2024 ReconVault. All rights reserved.</p>
                  </div>
                </motion.div>
              )}
              
              {/* Actions */}
              <div className="flex justify-end gap-3 mt-6">
                <Button variant="ghost" onClick={handleReset}>
                  Reset to Defaults
                </Button>
                <Button variant="primary" onClick={handleSave}>
                  Save Changes
                </Button>
              </div>
            </div>
          </div>
        </div>
      </MainContent>
    </Layout>
  );
};

export default SettingsPage;
