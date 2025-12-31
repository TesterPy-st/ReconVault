// ReconVault Badge Component

import React from 'react';
import { motion } from 'framer-motion';

const Badge = ({
  children,
  variant = 'default',
  size = 'medium',
  dot = false,
  removable = false,
  onRemove,
  className = '',
  ...props
}) => {
  const variants = {
    default: 'bg-cyber-lighter text-neon-green border-cyber-border',
    primary: 'bg-neon-green/20 text-neon-green border-neon-green/30',
    secondary: 'bg-neon-blue/20 text-neon-blue border-neon-blue/30',
    success: 'bg-green-500/20 text-green-500 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30',
    danger: 'bg-neon-pink/20 text-neon-pink border-neon-pink/30',
    purple: 'bg-neon-purple/20 text-neon-purple border-neon-purple/30',
    pending: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30',
    processing: 'bg-blue-500/20 text-blue-500 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-500 border-green-500/30',
    failed: 'bg-red-500/20 text-red-500 border-red-500/30',
    low: 'bg-green-500/20 text-green-500 border-green-500/30',
    medium: 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30',
    high: 'bg-orange-500/20 text-orange-500 border-orange-500/30',
    critical: 'bg-neon-pink/20 text-neon-pink border-neon-pink/30',
  };
  
  const sizes = {
    small: 'px-2 py-0.5 text-xs gap-1',
    medium: 'px-2.5 py-1 text-sm gap-1.5',
    large: 'px-3 py-1.5 text-base gap-2',
  };
  
  const colorMap = {
    default: 'text-neon-green',
    primary: 'text-neon-green',
    secondary: 'text-neon-blue',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    danger: 'text-neon-pink',
    purple: 'text-neon-purple',
    pending: 'text-yellow-500',
    processing: 'text-blue-500',
    completed: 'text-green-500',
    failed: 'text-red-500',
    low: 'text-green-500',
    medium: 'text-yellow-500',
    high: 'text-orange-500',
    critical: 'text-neon-pink',
  };
  
  const dotColors = {
    default: 'bg-neon-green',
    primary: 'bg-neon-green',
    secondary: 'bg-neon-blue',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-neon-pink',
    purple: 'bg-neon-purple',
    pending: 'bg-yellow-500',
    processing: 'bg-blue-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    low: 'bg-green-500',
    medium: 'bg-yellow-500',
    high: 'bg-orange-500',
    critical: 'bg-neon-pink',
  };
  
  return (
    <motion.span
      className={`
        inline-flex items-center font-medium rounded-full border
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.05 }}
      {...props}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]} ${
            size === 'small' ? 'w-1 h-1' : ''
          }`}
        />
      )}
      
      <span>{children}</span>
      
      {removable && (
        <button
          onClick={onRemove}
          className={`ml-1 ${colorMap[variant]} hover:opacity-70 transition-opacity ${
            size === 'small' ? 'text-xs' : ''
          }`}
          aria-label="Remove"
        >
          <svg
            className="w-3 h-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </motion.span>
  );
};

// Status Badge component with predefined statuses
Badge.Status = ({ status, size = 'small' }) => {
  const statusConfig = {
    pending: { label: 'Pending', variant: 'pending' },
    queued: { label: 'Queued', variant: 'processing' },
    processing: { label: 'Processing', variant: 'processing' },
    completed: { label: 'Completed', variant: 'completed' },
    failed: { label: 'Failed', variant: 'failed' },
    cancelled: { label: 'Cancelled', variant: 'default' },
    active: { label: 'Active', variant: 'success' },
    inactive: { label: 'Inactive', variant: 'default' },
    online: { label: 'Online', variant: 'success' },
    offline: { label: 'Offline', variant: 'default' },
  };
  
  const config = statusConfig[status] || { label: status, variant: 'default' };
  
  return (
    <Badge variant={config.variant} size={size} dot>
      {config.label}
    </Badge>
  );
};

// Risk Badge component with predefined risk levels
Badge.Risk = ({ score, size = 'small' }) => {
  let level, variant;
  
  if (score >= 80) {
    level = 'Critical';
    variant = 'critical';
  } else if (score >= 60) {
    level = 'High';
    variant = 'high';
  } else if (score >= 40) {
    level = 'Medium';
    variant = 'medium';
  } else {
    level = 'Low';
    variant = 'low';
  }
  
  return (
    <Badge variant={variant} size={size}>
      {level} ({score}%)
    </Badge>
  );
};

export default Badge;
