// ReconVault About Page

import React from 'react';
import { motion } from 'framer-motion';
import Layout from '../components/layout/Layout';
import MainContent from '../components/layout/MainContent';
import Button from '../components/ui/Button';
import targetStore from '../stores/targetStore';

const AboutPage = () => {
  const { stats, fetchStats } = targetStore();
  
  React.useEffect(() => {
    fetchStats();
  }, [fetchStats]);
  
  const features = [
    {
      icon: '🎯',
      title: 'Target Management',
      description: 'Create, organize, and manage reconnaissance targets with ease. Support for domains, IP addresses, emails, phone numbers, and more.',
    },
    {
      icon: '🕸️',
      title: 'Intelligence Graph',
      description: 'Visualize entity relationships with interactive force-directed graphs. Discover hidden connections and patterns.',
    },
    {
      icon: '🔍',
      title: 'OSINT Collection',
      description: 'Gather open-source intelligence from multiple sources including WHOIS, DNS, SSL certificates, and social media.',
    },
    {
      icon: '⚡',
      title: 'Real-time Updates',
      description: 'Monitor reconnaissance progress in real-time with live WebSocket updates and instant notifications.',
    },
    {
      icon: '📊',
      title: 'Risk Assessment',
      description: 'Automated risk scoring and vulnerability identification with detailed breakdowns and confidence levels.',
    },
    {
      icon: '🔒',
      title: 'Ethical Compliance',
      description: 'Built-in ethical guidelines and compliance framework to ensure responsible OSINT gathering.',
    },
  ];
  
  const techStack = [
    { category: 'Frontend', items: ['React 18', 'Vite', 'Tailwind CSS', 'Framer Motion', 'react-force-graph', 'D3.js'] },
    { category: 'Backend', items: ['FastAPI', 'Python 3.11', 'Uvicorn', 'Pydantic'] },
    { category: 'Database', items: ['PostgreSQL', 'Neo4j', 'Redis'] },
    { category: 'Infrastructure', items: ['Docker', 'Docker Compose', 'Nginx'] },
  ];
  
  return (
    <Layout>
      <MainContent>
        <div className="max-w-4xl mx-auto">
          {/* Hero section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="w-24 h-24 mx-auto rounded-xl bg-gradient-to-br from-neon-green to-neon-blue flex items-center justify-center mb-6">
              <span className="text-cyber-dark font-bold font-cyber text-3xl">RV</span>
            </div>
            <h1 className="text-4xl font-bold text-neon-green font-cyber mb-4">
              RECONVAULT
            </h1>
            <p className="text-xl text-cyber-gray mb-6">
              Cyber Reconnaissance Intelligence System
            </p>
            <p className="text-lg text-neon-blue font-mono mb-4">v0.1.0</p>
            
            <div className="flex items-center justify-center gap-4">
              <Button variant="primary">Get Started</Button>
              <Button variant="outline">View Documentation</Button>
            </div>
          </motion.div>
          
          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12"
          >
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6 text-center">
              <p className="text-3xl font-bold text-neon-green font-mono">{stats.total || 0}</p>
              <p className="text-sm text-cyber-gray">Total Targets</p>
            </div>
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6 text-center">
              <p className="text-3xl font-bold text-neon-blue font-mono">{stats.completed || 0}</p>
              <p className="text-sm text-cyber-gray">Completed</p>
            </div>
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6 text-center">
              <p className="text-3xl font-bold text-neon-purple font-mono">Active</p>
              <p className="text-sm text-cyber-gray">System Status</p>
            </div>
            <div className="bg-cyber-light rounded-lg border border-cyber-border p-6 text-center">
              <p className="text-3xl font-bold text-neon-pink font-mono">100%</p>
              <p className="text-sm text-cyber-gray">Operational</p>
            </div>
          </motion.div>
          
          {/* Features */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-12"
          >
            <h2 className="text-2xl font-bold text-neon-green font-cyber mb-6 text-center">
              Core Features
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 hover:border-neon-green/30 transition-colors group"
                >
                  <span className="text-3xl mb-4 block">{feature.icon}</span>
                  <h3 className="text-lg font-semibold text-neon-green mb-2 group-hover:text-neon-blue transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-cyber-gray">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
          
          {/* Tech stack */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-12"
          >
            <h2 className="text-2xl font-bold text-neon-green font-cyber mb-6 text-center">
              Technology Stack
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {techStack.map((stack) => (
                <div key={stack.category} className="bg-cyber-light rounded-lg border border-cyber-border p-6">
                  <h3 className="text-lg font-semibold text-neon-blue mb-4">{stack.category}</h3>
                  <ul className="space-y-2">
                    {stack.items.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-cyber-gray">
                        <span className="text-neon-green">▹</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </motion.div>
          
          {/* Development team */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mb-12"
          >
            <h2 className="text-2xl font-bold text-neon-green font-cyber mb-6 text-center">
              Development Team
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  name: 'Simanchala Bisoyi',
                  role: 'Lead Architect & Backend Developer',
                  initial: 'SB',
                  color: 'from-neon-green to-neon-blue',
                },
                {
                  name: 'Subham Mohanty',
                  role: 'Frontend Specialist & UI/UX Designer',
                  initial: 'SM',
                  color: 'from-neon-blue to-neon-purple',
                },
                {
                  name: 'Abhinav Kumar',
                  role: 'DevOps & Infrastructure Engineer',
                  initial: 'AK',
                  color: 'from-neon-purple to-neon-pink',
                },
              ].map((member) => (
                <div
                  key={member.name}
                  className="bg-cyber-light rounded-lg border border-cyber-border p-6 text-center hover:border-neon-green/30 transition-colors"
                >
                  <div
                    className={`w-20 h-20 mx-auto rounded-full bg-gradient-to-br ${member.color} flex items-center justify-center mb-4`}
                  >
                    <span className="text-cyber-dark font-bold font-cyber text-xl">
                      {member.initial}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-neon-green">{member.name}</h3>
                  <p className="text-sm text-cyber-gray mt-1">{member.role}</p>
                </div>
              ))}
            </div>
          </motion.div>
          
          {/* Links and resources */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="text-center"
          >
            <h2 className="text-2xl font-bold text-neon-green font-cyber mb-6">
              Resources
            </h2>
            <div className="flex flex-wrap justify-center gap-4">
              <Button variant="outline">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Documentation
              </Button>
              <Button variant="outline">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                GitHub
              </Button>
              <Button variant="outline">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
                Support
              </Button>
              <Button variant="outline">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Privacy Policy
              </Button>
            </div>
          </motion.div>
          
          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-12 pt-8 border-t border-cyber-border text-center"
          >
            <p className="text-cyber-gray">
              © 2024 ReconVault. All rights reserved.
            </p>
            <p className="text-sm text-cyber-gray mt-2">
              Cyber Reconnaissance Intelligence System | Built with ❤️
            </p>
          </motion.div>
        </div>
      </MainContent>
    </Layout>
  );
};

export default AboutPage;
