// ReconVault Input Component

import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';

const Input = forwardRef(({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  onBlur,
  onFocus,
  error,
  hint,
  disabled = false,
  required = false,
  leftIcon = null,
  rightIcon = null,
  name,
  id,
  autoComplete,
  maxLength,
  className = '',
  ...props
}, ref) => {
  const inputId = id || name;
  const errorId = `${inputId}-error`;
  const hintId = `${inputId}-hint`;
  
  const hasError = Boolean(error);
  
  return (
    <div className={`input-wrapper ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-neon-green mb-1.5"
        >
          {label}
          {required && <span className="text-neon-pink ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-cyber-gray">
            {leftIcon}
          </div>
        )}
        
        <motion.input
          ref={ref}
          type={type}
          id={inputId}
          name={name}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          onFocus={onFocus}
          disabled={disabled}
          required={required}
          autoComplete={autoComplete}
          maxLength={maxLength}
          aria-invalid={hasError}
          aria-describedby={
            [
              hasError ? errorId : null,
              hint ? hintId : null,
            ]
              .filter(Boolean)
              .join(' ') || undefined
          }
          className={`
            w-full bg-cyber-darker border rounded-lg px-4 py-3 text-neon-green
            placeholder-cyber-gray/50
            focus:outline-none focus:ring-2 focus:ring-neon-green/50
            transition-all duration-200
            ${leftIcon ? 'pl-10' : ''}
            ${rightIcon ? 'pr-10' : ''}
            ${
              hasError
                ? 'border-neon-pink focus:border-neon-pink focus:ring-neon-pink/50'
                : 'border-cyber-border focus:border-neon-green'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          whileFocus={{ scale: 1.01 }}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-cyber-gray">
            {rightIcon}
          </div>
        )}
      </div>
      
      {hasError && (
        <motion.p
          id={errorId}
          className="mt-1.5 text-sm text-neon-pink flex items-center gap-1"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </motion.p>
      )}
      
      {hint && !hasError && (
        <p id={hintId} className="mt-1.5 text-sm text-cyber-gray">
          {hint}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
