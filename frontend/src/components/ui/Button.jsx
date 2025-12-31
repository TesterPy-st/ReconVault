// ReconVault Button Component

import React from 'react';
import { motion } from 'framer-motion';

const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  fullWidth = false,
  leftIcon = null,
  rightIcon = null,
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseStyles = `
    inline-flex items-center justify-center font-bold rounded-lg
    transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-cyber-dark
    disabled:opacity-50 disabled:cursor-not-allowed
    relative overflow-hidden
  `;
  
  const variants = {
    primary: `
      bg-neon-green text-cyber-dark
      hover:bg-opacity-80 hover:shadow-neon
      focus:ring-neon-green
    `,
    secondary: `
      bg-neon-blue text-cyber-dark
      hover:bg-opacity-80 hover:shadow-neon-glow
      focus:ring-neon-blue
    `,
    danger: `
      bg-neon-pink text-white
      hover:bg-opacity-80
      focus:ring-neon-pink
    `,
    outline: `
      border-2 border-neon-green text-neon-green
      bg-transparent hover:bg-neon-green/10
      focus:ring-neon-green
    `,
    ghost: `
      text-neon-green bg-transparent
      hover:bg-neon-green/10
      focus:ring-neon-green
    `,
    warning: `
      bg-yellow-500 text-cyber-dark
      hover:bg-opacity-80
      focus:ring-yellow-500
    `,
    success: `
      bg-green-500 text-cyber-dark
      hover:bg-opacity-80
      focus:ring-green-500
    `,
  };
  
  const sizes = {
    small: 'px-3 py-1.5 text-sm gap-1.5',
    medium: 'px-4 py-2 text-base gap-2',
    large: 'px-6 py-3 text-lg gap-2',
  };
  
  const widthClass = fullWidth ? 'w-full' : '';
  
  const isDisabled = disabled || loading;
  
  return (
    <motion.button
      type={type}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${widthClass} ${className}`}
      onClick={onClick}
      disabled={isDisabled}
      whileTap={{ scale: isDisabled ? 1 : 0.98 }}
      whileHover={{ scale: isDisabled ? 1 : 1.02 }}
      {...props}
    >
      {loading && (
        <motion.svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </motion.svg>
      )}
      
      {!loading && leftIcon && (
        <span className="button-icon">{leftIcon}</span>
      )}
      
      <span className="button-text">{children}</span>
      
      {!loading && rightIcon && (
        <span className="button-icon">{rightIcon}</span>
      )}
      
      {/* Glow effect overlay */}
      <div className="absolute inset-0 rounded-lg opacity-0 hover:opacity-100 pointer-events-none transition-opacity duration-200">
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-neon-green/20 via-neon-blue/20 to-neon-purple/20 animate-pulse" />
      </div>
    </motion.button>
  );
};

export default Button;
