// ReconVault TargetForm Component

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Button from '../ui/Button';
import targetStore from '../../stores/targetStore';
import uiStore from '../../stores/uiStore';
import { TARGET_TYPES } from '../../utils/constants';
import { validateTarget } from '../../utils/validators';

const TargetForm = ({ isOpen, onClose, target = null }) => {
  const { createTarget, updateTarget, loading } = targetStore();
  const { showSuccess, showError } = uiStore();
  
  const isEditing = Boolean(target);
  
  const [formData, setFormData] = useState({
    type: TARGET_TYPES.DOMAIN,
    value: '',
    source: '',
    description: '',
  });
  
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    if (target) {
      setFormData({
        type: target.type || TARGET_TYPES.DOMAIN,
        value: target.value || '',
        source: target.source || '',
        description: target.description || '',
      });
    } else {
      setFormData({
        type: TARGET_TYPES.DOMAIN,
        value: '',
        source: '',
        description: '',
      });
    }
    setErrors({});
  }, [target, isOpen]);
  
  const targetTypeOptions = [
    { value: TARGET_TYPES.DOMAIN, label: 'Domain' },
    { value: TARGET_TYPES.IP_ADDRESS, label: 'IP Address' },
    { value: TARGET_TYPES.EMAIL, label: 'Email' },
    { value: TARGET_TYPES.PHONE, label: 'Phone' },
    { value: TARGET_TYPES.SOCIAL_MEDIA, label: 'Social Media' },
    { value: TARGET_TYPES.PERSON, label: 'Person' },
    { value: TARGET_TYPES.ORGANIZATION, label: 'Organization' },
    { value: TARGET_TYPES.KEYWORD, label: 'Keyword' },
    { value: TARGET_TYPES.FILE, label: 'File' },
    { value: TARGET_TYPES.WIFI, label: 'WiFi Network' },
  ];
  
  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    
    // Clear error when field changes
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };
  
  const validate = () => {
    const validation = validateTarget(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return false;
    }
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    try {
      if (isEditing) {
        await updateTarget(target.id, formData);
        showSuccess('Target updated successfully');
      } else {
        await createTarget(formData);
        showSuccess('Target created successfully');
      }
      onClose();
    } catch (error) {
      showError(error.response?.data?.message || 'Failed to save target');
    }
  };
  
  const handleCancel = () => {
    setFormData({
      type: TARGET_TYPES.DOMAIN,
      value: '',
      source: '',
      description: '',
    });
    setErrors({});
    onClose();
  };
  
  const getInputHint = () => {
    switch (formData.type) {
      case TARGET_TYPES.DOMAIN:
        return 'e.g., example.com';
      case TARGET_TYPES.IP_ADDRESS:
        return 'e.g., 192.168.1.1';
      case TARGET_TYPES.EMAIL:
        return 'e.g., user@example.com';
      case TARGET_TYPES.PHONE:
        return 'e.g., +1234567890';
      case TARGET_TYPES.SOCIAL_MEDIA:
        return 'e.g., @username or profile URL';
      case TARGET_TYPES.PERSON:
        return 'e.g., John Doe';
      case TARGET_TYPES.ORGANIZATION:
        return 'e.g., Company Name';
      default:
        return 'Enter target value';
    }
  };
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title={isEditing ? 'Edit Target' : 'Create New Target'}
      size="medium"
      footer={
        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={handleCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} loading={loading}>
            {isEditing ? 'Update Target' : 'Create Target'}
          </Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Select
          label="Target Type"
          name="type"
          value={formData.type}
          onChange={(value) => handleChange('type', value)}
          options={targetTypeOptions}
          required
          error={errors.type}
        />
        
        <Input
          label="Target Value"
          name="value"
          type="text"
          value={formData.value}
          onChange={(e) => handleChange('value', e.target.value)}
          placeholder={getInputHint()}
          required
          error={errors.value}
          autoFocus
        />
        
        <Input
          label="Source (Optional)"
          name="source"
          type="url"
          value={formData.source}
          onChange={(e) => handleChange('source', e.target.value)}
          placeholder="https://..."
          hint="URL where this target was found"
          error={errors.source}
        />
        
        <div className="form-group">
          <label className="block text-sm font-medium text-neon-green mb-1.5">
            Description (Optional)
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Add notes about this target..."
            rows={3}
            className="w-full bg-cyber-darker border border-cyber-border rounded-lg px-4 py-3 text-neon-green placeholder-cyber-gray/50 focus:outline-none focus:border-neon-green focus:ring-1 focus:ring-neon-green resize-none"
          />
        </div>
        
        {/* Quick tips */}
        <div className="bg-cyber-darker/50 rounded-lg p-3 border border-cyber-border">
          <h4 className="text-sm font-medium text-neon-green mb-2">Quick Tips</h4>
          <ul className="text-xs text-cyber-gray space-y-1">
            <li>• Use domain type for website reconnaissance</li>
            <li>• IP address type for network scanning</li>
            <li>• Email type for social engineering assessment</li>
            <li>• Organization type for corporate OSINT</li>
          </ul>
        </div>
      </form>
    </Modal>
  );
};

export default TargetForm;
