import { motion } from 'framer-motion'

function App() {
  return (
    <div className="min-h-screen bg-dark-900">
      {/* Header */}
      <header className="border-b border-dark-600 bg-dark-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center space-x-3"
            >
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-neon-green to-neon-blue flex items-center justify-center shadow-neon-green">
                <span className="text-dark-900 font-bold text-xl">R</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-wider">RECONVAULT</h1>
                <p className="text-xs text-neon-blue font-mono">CYBER INTELLIGENCE</p>
              </div>
            </motion.div>

            <motion.nav
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex items-center space-x-6"
            >
              <a href="#" className="text-gray-300 hover:text-neon-green transition-colors text-sm font-medium">
                Dashboard
              </a>
              <a href="#" className="text-gray-300 hover:text-neon-green transition-colors text-sm font-medium">
                Graph
              </a>
              <a href="#" className="text-gray-300 hover:text-neon-green transition-colors text-sm font-medium">
                Reports
              </a>
              <a href="#" className="text-gray-300 hover:text-neon-green transition-colors text-sm font-medium">
                Settings
              </a>
            </motion.nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center py-20"
        >
          <div className="mb-8">
            <motion.div
              animate={{ 
                boxShadow: ['0 0 20px rgba(0, 255, 136, 0.3)', '0 0 40px rgba(0, 255, 136, 0.6)', '0 0 20px rgba(0, 255, 136, 0.3)'],
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="inline-block p-8 rounded-2xl bg-dark-800 border border-dark-600"
            >
              <div className="text-6xl mb-4">🔍</div>
              <h2 className="text-3xl font-bold text-white mb-2">ReconVault</h2>
              <p className="text-neon-blue font-mono text-sm">System Initialization Complete</p>
            </motion.div>
          </div>

          <div className="max-w-2xl mx-auto space-y-6">
            <p className="text-gray-300 text-lg">
              Welcome to ReconVault - A cyber reconnaissance intelligence system with graph-based UI and modular OSINT pipeline.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              {[
                { icon: '📊', title: 'Graph Analysis', desc: 'Visual intelligence correlations' },
                { icon: '🤖', title: 'AI Engine', desc: 'Automated pattern recognition' },
                { icon: '🛡️', title: 'Risk Assessment', desc: 'Threat scoring system' },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                  className="p-6 rounded-xl bg-dark-800 border border-dark-600 hover:border-neon-green transition-all hover:shadow-neon-green"
                >
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="text-white font-semibold mb-1">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.desc}</p>
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="mt-12 p-4 rounded-lg bg-dark-800/50 border border-dark-600"
            >
              <p className="text-sm text-neon-green font-mono">
                ✓ Frontend initialized on port 5173
              </p>
              <p className="text-sm text-neon-blue font-mono">
                ✓ Backend API ready on port 8000
              </p>
              <p className="text-sm text-neon-purple font-mono">
                ✓ All services operational
              </p>
            </motion.div>
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-600 bg-dark-800/30 mt-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <p>© 2024 ReconVault. Cyber Intelligence System.</p>
            <p className="font-mono text-neon-blue">v0.1.0</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
