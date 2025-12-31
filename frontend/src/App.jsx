// ReconVault Main Application Component
import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import './styles/main.css'

// Main Application Component
function App() {
  const [healthStatus, setHealthStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Check backend health on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        console.log('Checking backend health...')
        const response = await axios.get('/api/health')
        setHealthStatus(response.data)
        console.log('Backend health check successful:', response.data)
      } catch (err) {
        console.error('Backend health check failed:', err)
        setError('Backend service unavailable')
      } finally {
        setLoading(false)
      }
    }
    
    checkBackendHealth()
  }, [])
  
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }
  
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 100 }
    }
  }
  
  return (
    <div className="min-h-screen bg-cyber-dark text-neon-green font-mono overflow-hidden">
      {/* Background Grid */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-cyber-dark to-cyber-darker"></div>
        <div className="absolute inset-0 bg-[url('/grid.png')] opacity-10"></div>
      </div>
      
      {/* Main Content */}
      <motion.div
        className="container mx-auto px-4 py-8 max-w-6xl"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.header
          className="text-center mb-12"
          variants={itemVariants}
        >
          <h1 className="text-4xl md:text-6xl font-cyber font-bold mb-4">
            <span className="text-neon-green">RECON</span>
            <span className="text-neon-blue">VAULT</span>
          </h1>
          <p className="text-cyber-gray text-lg md:text-xl">
            Cyber Reconnaissance Intelligence System
          </p>
          <div className="w-32 h-1 bg-neon-green mx-auto mt-4 rounded-full"></div>
        </motion.header>
        
        {/* Main Content Area */}
        <motion.main className="bg-cyber-light rounded-lg p-6 mb-8 border border-cyber-border" variants={itemVariants}>
          <h2 className="text-2xl font-bold mb-6 text-neon-green">System Status</h2>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-pulse text-neon-blue text-lg">
                Loading system status...
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="text-red-500 text-lg mb-4">⚠️ {error}</div>
              <p className="text-cyber-gray">
                The backend service may still be starting up. Please wait a moment and refresh.
              </p>
            </div>
          ) : healthStatus ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* System Info Card */}
              <motion.div
                className="bg-cyber-darker p-6 rounded-lg border border-cyber-border"
                whileHover={{ scale: 1.02 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <h3 className="text-xl font-bold mb-4 text-neon-green">System Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-cyber-gray">Status:</span>
                    <span className={`font-mono ${healthStatus.status === 'healthy' ? 'text-neon-green' : 'text-red-500'}`}>
                      {healthStatus.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-cyber-gray">Service:</span>
                    <span className="text-neon-blue font-mono">{healthStatus.service}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-cyber-gray">Version:</span>
                    <span className="text-neon-purple font-mono">{healthStatus.version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-cyber-gray">Timestamp:</span>
                    <span className="text-cyber-gray font-mono text-sm">{new Date(healthStatus.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </motion.div>
              
              {/* Features Card */}
              <motion.div
                className="bg-cyber-darker p-6 rounded-lg border border-cyber-border"
                whileHover={{ scale: 1.02 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <h3 className="text-xl font-bold mb-4 text-neon-green">Phase 1 Features</h3>
                <ul className="space-y-2 text-cyber-gray">
                  <li className="flex items-center">
                    <span className="text-neon-green mr-2">▹</span>
                    FastAPI Backend Infrastructure
                  </li>
                  <li className="flex items-center">
                    <span className="text-neon-blue mr-2">▹</span>
                    React + Vite Frontend
                  </li>
                  <li className="flex items-center">
                    <span className="text-neon-purple mr-2">▹</span>
                    Docker Containerization
                  </li>
                  <li className="flex items-center">
                    <span className="text-neon-pink mr-2">▹</span>
                    PostgreSQL & Neo4j Integration
                  </li>
                  <li className="flex items-center">
                    <span className="text-neon-green mr-2">▹</span>
                    Nginx Reverse Proxy
                  </li>
                </ul>
              </motion.div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-yellow-500 text-lg">⚠️ Unable to retrieve system status</div>
            </div>
          )}
        </motion.main>
        
        {/* Footer */}
        <motion.footer
          className="text-center text-cyber-gray text-sm py-6 border-t border-cyber-border"
          variants={itemVariants}
        >
          <p>ReconVault v0.1.0 | Cyber Reconnaissance Intelligence System</p>
          <p className="mt-2">Developed by Simanchala Bisoyi, Subham Mohanty, Abhinav Kumar</p>
          <div className="mt-4">
            <span className="text-neon-green">●</span>
            <span className="ml-2 text-cyber-gray">System Operational</span>
          </div>
        </motion.footer>
      </motion.div>
      
      {/* Background Animation */}
      <div className="fixed inset-0 pointer-events-none -z-20">
        <div className="absolute top-10 left-10 w-2 h-2 bg-neon-green rounded-full animate-pulse-slow"></div>
        <div className="absolute top-20 right-20 w-1 h-1 bg-neon-blue rounded-full animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-20 left-20 w-1 h-1 bg-neon-purple rounded-full animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-10 right-10 w-2 h-2 bg-neon-pink rounded-full animate-pulse-slow" style={{ animationDelay: '3s' }}></div>
      </div>
    </div>
  )
}

export default App
