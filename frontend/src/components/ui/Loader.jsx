// ReconVault Loader Component

import React from 'react';
import { motion } from 'framer-motion';

const Loader = ({
  size = 'medium',
  variant = 'default',
  text = '',
  fullScreen = false,
  className = '',
}) => {
  const sizes = {
    small: { spinner: 'w-6 h-6', text: 'text-sm' },
    medium: { spinner: 'w-10 h-10', text: 'text-base' },
    large: { spinner: 'w-16 h-16', text: 'text-lg' },
  };
  
  const variants = {
    default: 'border-neon-green border-t-transparent',
    primary: 'border-neon-blue border-t-transparent',
    secondary: 'border-neon-purple border-t-transparent',
    success: 'border-green-500 border-t-transparent',
    warning: 'border-yellow-500 border-t-transparent',
    danger: 'border-neon-pink border-t-transparent',
  };
  
  const containerClass = fullScreen
    ? 'fixed inset-0 z-50 flex items-center justify-center bg-cyber-dark/80 backdrop-blur-sm'
    : 'flex flex-col items-center justify-center';
  
  const spinner = (
    <motion.div
      className={`
        ${sizes[size].spinner} rounded-full border-4
        ${variants[variant]}
      `}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    />
  );
  
  const pulseSpinner = (
    <div className="relative">
      <motion.div
        className={`${sizes[size].spinner} rounded-full border-4 border-cyber-border`}
      />
      <motion.div
        className={`
          absolute inset-0 ${sizes[size].spinner} rounded-full border-4 border-transparent
          ${variants[variant]}
        `}
        animate={{
          scale: [1, 1.2],
          opacity: [1, 0],
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'easeOut',
        }}
      />
    </div>
  );
  
  const dotsLoader = (
    <div className="flex gap-2">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`${sizes[size].spinner} rounded-full ${variants[variant]}`}
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.2,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
  
  const barsLoader = (
    <div className="flex gap-1 h-8 items-end">
      {[0, 1, 2, 3, 4].map((index) => (
        <motion.div
          key={index}
          className={`w-2 ${variants[variant]} bg-current rounded-t`}
          animate={{
            height: ['40%', '100%', '40%'],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.1,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
  
  const ringLoader = (
    <motion.div
      className={`
        relative ${sizes[size].spinner}
      `}
    >
      <motion.div
        className={`absolute inset-0 rounded-full border-4 border-cyber-border`}
      />
      <motion.div
        className={`absolute inset-0 rounded-full border-4 border-transparent border-t-current ${variants[variant]}`}
        style={{ borderTopColor: 'currentColor' }}
        animate={{ rotate: 360 }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      <motion.div
        className={`absolute inset-1 rounded-full border-4 border-transparent border-b-current ${variants[variant]}`}
        style={{ borderBottomColor: 'currentColor' }}
        animate={{ rotate: -360 }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </motion.div>
  );
  
  const renderLoader = () => {
    switch (variant) {
      case 'pulse':
        return pulseSpinner;
      case 'dots':
        return dotsLoader;
      case 'bars':
        return barsLoader;
      case 'ring':
        return ringLoader;
      default:
        return spinner;
    }
  };
  
  return (
    <div className={`${containerClass} ${className}`}>
      {renderLoader()}
      
      {text && (
        <motion.p
          className={`mt-4 text-neon-green ${sizes[size].text}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {text}
        </motion.p>
      )}
    </div>
  );
};

// Skeleton loader component
Loader.Skeleton = ({ width, height, className = '', variant = 'default' }) => {
  const variants = {
    default: 'bg-cyber-darker',
    card: 'bg-cyber-light',
    input: 'bg-cyber-darker',
  };
  
  return (
    <div
      className={`${variants[variant]} rounded animate-pulse ${className}`}
      style={{ width, height }}
    />
  );
};

// Skeleton card
Loader.SkeletonCard = ({ className = '' }) => (
  <div className={`bg-cyber-light rounded-lg p-6 border border-cyber-border ${className}`}>
    <div className="flex items-center gap-4 mb-4">
      <Loader.Skeleton width="48px" height="48px" variant="card" />
      <div className="flex-1">
        <Loader.Skeleton width="60%" height="20px" className="mb-2" />
        <Loader.Skeleton width="40%" height="16px" />
      </div>
    </div>
    <Loader.Skeleton width="100%" height="16px" className="mb-2" />
    <Loader.Skeleton width="80%" height="16px" />
  </div>
);

export default Loader;
