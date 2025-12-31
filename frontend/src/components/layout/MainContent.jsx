// ReconVault MainContent Component

import React from 'react';
import { motion } from 'framer-motion';

const MainContent = ({ children, className = '', noPadding = false }) => {
  return (
    <motion.main
      className={`
        flex-1 min-h-screen
        ${noPadding ? '' : 'p-4 lg:p-6'}
        ${className}
      `}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.main>
  );
};

export default MainContent;
