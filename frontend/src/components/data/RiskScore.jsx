// ReconVault RiskScore Component

import React from 'react';
import { motion } from 'framer-motion';

const RiskScore = ({ score = 0, size = 'medium', showLabel = true, className = '' }) => {
  const getColor = (score) => {
    if (score >= 80) return { color: '#ff006e', bg: 'bg-neon-pink' };
    if (score >= 60) return { color: '#ff6600', bg: 'bg-orange-500' };
    if (score >= 40) return { color: '#ffcc00', bg: 'bg-yellow-500' };
    return { color: '#00ff88', bg: 'bg-neon-green' };
  };
  
  const getLabel = (score) => {
    if (score >= 80) return 'Critical';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  };
  
  const getSizeConfig = (size) => {
    const configs = {
      small: { ring: 40, stroke: 4, text: 'text-sm' },
      medium: { ring: 60, stroke: 6, text: 'text-lg' },
      large: { ring: 100, stroke: 8, text: 'text-2xl' },
      xlarge: { ring: 150, stroke: 12, text: 'text-4xl' },
    };
    return configs[size] || configs.medium;
  };
  
  const config = getSizeConfig(size);
  const { color, bg } = getColor(score);
  const circumference = 2 * Math.PI * ((config.ring - config.stroke) / 2);
  
  // Calculate dash array for the progress ring
  const dashArray = circumference;
  const dashOffset = circumference - (score / 100) * circumference;
  
  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative" style={{ width: config.ring, height: config.ring }}>
        {/* Background ring */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx={config.ring / 2}
            cy={config.ring / 2}
            r={(config.ring - config.stroke) / 2}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.stroke}
            className="text-cyber-darker"
          />
          
          {/* Progress ring */}
          <motion.circle
            cx={config.ring / 2}
            cy={config.ring / 2}
            r={(config.ring - config.stroke) / 2}
            fill="none"
            stroke={color}
            strokeWidth={config.stroke}
            strokeLinecap="round"
            strokeDasharray={dashArray}
            initial={{ strokeDashoffset: dashArray }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={`${config.text} font-bold font-mono`}
            style={{ color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            {Math.round(score)}%
          </motion.span>
        </div>
        
        {/* Glow effect */}
        <div
          className="absolute inset-0 rounded-full opacity-20"
          style={{
            background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
            filter: 'blur(10px)',
          }}
        />
      </div>
      
      {showLabel && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-2"
        >
          <span
            className={`text-sm font-medium uppercase tracking-wider`}
            style={{ color }}
          >
            {getLabel(score)} Risk
          </span>
        </motion.div>
      )}
    </div>
  );
};

// Compact risk score (just a colored badge with score)
RiskScore.Compact = ({ score = 0, showLabel = true, className = '' }) => {
  const getColor = (score) => {
    if (score >= 80) return { color: '#ff006e', bg: 'bg-neon-pink/20', text: 'text-neon-pink' };
    if (score >= 60) return { color: '#ff6600', bg: 'bg-orange-500/20', text: 'text-orange-500' };
    if (score >= 40) return { color: '#ffcc00', bg: 'bg-yellow-500/20', text: 'text-yellow-500' };
    return { color: '#00ff88', bg: 'bg-neon-green/20', text: 'text-neon-green' };
  };
  
  const { color, bg, text } = getColor(score);
  
  return (
    <div
      className={`inline-flex items-center gap-2 px-2 py-1 rounded-full ${bg} ${className}`}
    >
      <div
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: color }}
      />
      <span className={`text-sm font-mono font-bold ${text}`}>
        {Math.round(score)}%
      </span>
      {showLabel && (
        <span className={`text-xs uppercase ${text}`}>
          {score >= 80 ? 'Critical' : score >= 60 ? 'High' : score >= 40 ? 'Medium' : 'Low'}
        </span>
      )}
    </div>
  );
};

// Risk indicator bar
RiskScore.Bar = ({ score = 0, className = '' }) => {
  const getColor = (score) => {
    if (score >= 80) return '#ff006e';
    if (score >= 60) return '#ff6600';
    if (score >= 40) return '#ffcc00';
    return '#00ff88';
  };
  
  const color = getColor(score);
  
  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-cyber-gray">Risk Level</span>
        <span className="font-mono" style={{ color }}>{Math.round(score)}%</span>
      </div>
      <div className="h-2 bg-cyber-darker rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <div className="flex justify-between mt-1 text-[10px] text-cyber-gray">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
        <span>Critical</span>
      </div>
    </div>
  );
};

export default RiskScore;
