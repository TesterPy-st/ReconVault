// ReconVault Select Component

import React, { forwardRef, useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Select = forwardRef(({
  label,
  options = [],
  value,
  onChange,
  onBlur,
  error,
  disabled = false,
  required = false,
  placeholder = 'Select an option',
  name,
  id,
  className = '',
  emptyMessage = 'No options available',
  searchable = false,
  ...props
}, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef(null);
  const selectId = id || name;
  
  const selectedOption = options.find((opt) => opt.value === value);
  
  const filteredOptions = searchable && searchTerm
    ? options.filter((opt) =>
        opt.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;
  
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const handleSelect = (option) => {
    onChange?.(option.value, option);
    setIsOpen(false);
    setSearchTerm('');
  };
  
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setIsOpen(true);
    } else if (event.key === 'Escape') {
      setIsOpen(false);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      setIsOpen(true);
    }
  };
  
  return (
    <div className={`select-wrapper ${className}`} ref={containerRef}>
      {label && (
        <label
          htmlFor={selectId}
          className="block text-sm font-medium text-neon-green mb-1.5"
        >
          {label}
          {required && <span className="text-neon-pink ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <motion.button
          type="button"
          id={selectId}
          ref={ref}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          onBlur={onBlur}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className={`
            w-full bg-cyber-darker border rounded-lg px-4 py-3 text-left
            flex items-center justify-between
            focus:outline-none focus:ring-2 focus:ring-neon-green/50
            transition-all duration-200 cursor-pointer
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            ${
              error
                ? 'border-neon-pink focus:border-neon-pink'
                : 'border-cyber-border focus:border-neon-green'
            }
          `}
          whileTap={{ scale: 0.99 }}
        >
          <span className={selectedOption ? 'text-neon-green' : 'text-cyber-gray'}>
            {selectedOption?.label || placeholder}
          </span>
          
          <svg
            className={`w-5 h-5 text-cyber-gray transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </motion.button>
        
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute z-50 w-full mt-2 bg-cyber-light border border-cyber-border rounded-lg shadow-xl overflow-hidden"
            >
              {searchable && (
                <div className="p-2 border-b border-cyber-border">
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-cyber-darker border border-cyber-border rounded-lg px-3 py-2 text-neon-green text-sm focus:outline-none focus:border-neon-green"
                    onKeyDown={(e) => e.stopPropagation()}
                  />
                </div>
              )}
              
              <div className="max-h-60 overflow-y-auto">
                {filteredOptions.length > 0 ? (
                  filteredOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => handleSelect(option)}
                      className={`
                        w-full px-4 py-3 text-left transition-colors
                        flex items-center gap-2
                        ${
                          option.value === value
                            ? 'bg-neon-green/20 text-neon-green'
                            : 'text-cyber-gray hover:bg-cyber-darker hover:text-neon-green'
                        }
                      `}
                    >
                      {option.icon && <span>{option.icon}</span>}
                      <span>{option.label}</span>
                      {option.value === value && (
                        <svg
                          className="w-4 h-4 ml-auto"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-cyber-gray text-center">
                    {emptyMessage}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1.5 text-sm text-neon-pink flex items-center gap-1"
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
    </div>
  );
});

Select.displayName = 'Select';

export default Select;
