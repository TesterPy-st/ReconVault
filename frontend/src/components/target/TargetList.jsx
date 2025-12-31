// ReconVault TargetList Component

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import targetStore from '../../stores/targetStore';
import TargetCard from './TargetCard';
import Loader from '../ui/Loader';
import Button from '../ui/Button';

const TargetList = ({ onSelectTarget, onEditTarget }) => {
  const {
    targets,
    loading,
    pagination,
    filters,
    setPagination,
    setFilters,
    fetchTargets,
    searchTargets,
  } = targetStore();
  
  const [localSearch, setLocalSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  useEffect(() => {
    fetchTargets();
  }, [fetchTargets, pagination.page, filters]);
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (localSearch.trim()) {
      searchTargets(localSearch);
    } else {
      fetchTargets();
    }
  };
  
  const handlePageChange = (newPage) => {
    setPagination({ page: newPage });
  };
  
  const handleFilterChange = (key, value) => {
    setFilters({ [key]: value || null });
    setPagination({ page: 1 });
  };
  
  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'queued', label: 'Queued' },
    { value: 'processing', label: 'Processing' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ];
  
  const typeOptions = [
    { value: '', label: 'All Types' },
    { value: 'domain', label: 'Domain' },
    { value: 'ip_address', label: 'IP Address' },
    { value: 'email', label: 'Email' },
    { value: 'phone', label: 'Phone' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'person', label: 'Person' },
    { value: 'organization', label: 'Organization' },
  ];
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-xl font-bold text-neon-green font-cyber">
          Reconnaissance Targets
        </h2>
        <Button variant="primary" onClick={() => onSelectTarget?.(null)}>
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Target
        </Button>
      </div>
      
      {/* Search and filters */}
      <div className="bg-cyber-light rounded-lg border border-cyber-border p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <input
                type="text"
                value={localSearch}
                onChange={(e) => setLocalSearch(e.target.value)}
                placeholder="Search targets..."
                className="w-full bg-cyber-darker border border-cyber-border rounded-lg pl-10 pr-4 py-2.5 text-neon-green placeholder-cyber-gray/50 focus:outline-none focus:border-neon-green"
              />
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-cyber-gray"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </form>
          
          {/* Filter toggle (mobile) */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="lg:hidden px-4 py-2.5 bg-cyber-darker border border-cyber-border rounded-lg text-cyber-gray hover:text-neon-green"
          >
            Filters
          </button>
          
          {/* Filters */}
          <div className={`${showFilters ? 'block' : 'hidden lg:flex'} gap-3`}>
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="bg-cyber-darker border border-cyber-border rounded-lg px-4 py-2.5 text-neon-green focus:outline-none focus:border-neon-green"
            >
              {statusOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            
            <select
              value={filters.type || ''}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="bg-cyber-darker border border-cyber-border rounded-lg px-4 py-2.5 text-neon-green focus:outline-none focus:border-neon-green"
            >
              {typeOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Loading state */}
      {loading && (
        <div className="py-12">
          <Loader size="large" text="Loading targets..." />
        </div>
      )}
      
      {/* Empty state */}
      {!loading && targets.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-cyber-light rounded-lg border border-cyber-border p-12 text-center"
        >
          <svg
            className="w-16 h-16 mx-auto text-cyber-gray mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <h3 className="text-xl font-bold text-neon-green mb-2">No targets found</h3>
          <p className="text-cyber-gray mb-6">
            Get started by creating your first reconnaissance target
          </p>
          <Button variant="primary" onClick={() => onSelectTarget?.(null)}>
            Create First Target
          </Button>
        </motion.div>
      )}
      
      {/* Target grid */}
      {!loading && targets.length > 0 && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {targets.map((target, index) => (
              <motion.div
                key={target.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <TargetCard
                  target={target}
                  onClick={() => onSelectTarget?.(target)}
                  onEdit={() => onEditTarget?.(target)}
                />
              </motion.div>
            ))}
          </div>
          
          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-6">
              <Button
                variant="ghost"
                size="small"
                disabled={pagination.page === 1}
                onClick={() => handlePageChange(pagination.page - 1)}
              >
                Previous
              </Button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                  let pageNum;
                  if (pagination.totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (pagination.page <= 3) {
                    pageNum = i + 1;
                  } else if (pagination.page >= pagination.totalPages - 2) {
                    pageNum = pagination.totalPages - 4 + i;
                  } else {
                    pageNum = pagination.page - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`
                        w-10 h-10 rounded-lg font-medium transition-colors
                        ${
                          pagination.page === pageNum
                            ? 'bg-neon-green text-cyber-dark'
                            : 'bg-cyber-light text-cyber-gray hover:text-neon-green'
                        }
                      `}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <Button
                variant="ghost"
                size="small"
                disabled={pagination.page === pagination.totalPages}
                onClick={() => handlePageChange(pagination.page + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TargetList;
