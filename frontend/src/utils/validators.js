// ReconVault Validation Functions

import { TARGET_TYPES, ENTITY_TYPES } from './constants';

/**
 * Validate email address
 */
export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate domain name
 */
export function validateDomain(domain) {
  const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z0-9][a-zA-Z0-9-]*)*\.[a-zA-Z]{2,}$/;
  return domainRegex.test(domain);
}

/**
 * Validate IPv4 address
 */
export function validateIPv4(ip) {
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ipv4Regex.test(ip)) return false;
  
  const parts = ip.split('.').map(Number);
  return parts.every(part => part >= 0 && part <= 255);
}

/**
 * Validate IPv6 address
 */
export function validateIPv6(ip) {
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,7}:$|^([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$|^([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}$|^([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}$|^([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}$|^([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}$|^[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})$|^:((:[0-9a-fA-F]{1,4}){1,7}|:)$/;
  return ipv6Regex.test(ip);
}

/**
 * Validate phone number
 */
export function validatePhone(phone) {
  const phoneRegex = /^\+?[0-9]{10,15}$/;
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

/**
 * Validate URL
 */
export function validateUrl(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate target type
 */
export function validateTargetType(type) {
  return Object.values(TARGET_TYPES).includes(type);
}

/**
 * Validate entity type
 */
export function validateEntityType(type) {
  return Object.values(ENTITY_TYPES).includes(type);
}

/**
 * Validate target form data
 */
export function validateTarget(data) {
  const errors = {};
  
  if (!data.type) {
    errors.type = 'Target type is required';
  } else if (!validateTargetType(data.type)) {
    errors.type = 'Invalid target type';
  }
  
  if (!data.value) {
    errors.value = 'Target value is required';
  } else {
    switch (data.type) {
      case TARGET_TYPES.DOMAIN:
        if (!validateDomain(data.value)) {
          errors.value = 'Invalid domain format';
        }
        break;
      case TARGET_TYPES.EMAIL:
        if (!validateEmail(data.value)) {
          errors.value = 'Invalid email format';
        }
        break;
      case TARGET_TYPES.IP_ADDRESS:
        if (!validateIPv4(data.value) && !validateIPv6(data.value)) {
          errors.value = 'Invalid IP address format';
        }
        break;
      case TARGET_TYPES.PHONE:
        if (!validatePhone(data.value)) {
          errors.value = 'Invalid phone number format';
        }
        break;
    }
  }
  
  if (data.source && !validateUrl(data.source) && data.source.trim() !== '') {
    errors.source = 'Invalid source URL format';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate entity form data
 */
export function validateEntity(data) {
  const errors = {};
  
  if (!data.type) {
    errors.type = 'Entity type is required';
  } else if (!validateEntityType(data.type)) {
    errors.type = 'Invalid entity type';
  }
  
  if (!data.name) {
    errors.name = 'Entity name is required';
  } else if (data.name.length < 2) {
    errors.name = 'Entity name must be at least 2 characters';
  } else if (data.name.length > 200) {
    errors.name = 'Entity name must be less than 200 characters';
  }
  
  if (data.risk_score !== undefined) {
    if (data.risk_score < 0 || data.risk_score > 100) {
      errors.risk_score = 'Risk score must be between 0 and 100';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate search query
 */
export function validateSearchQuery(query) {
  const errors = {};
  
  if (!query || query.trim() === '') {
    errors.query = 'Search query is required';
  } else if (query.length < 2) {
    errors.query = 'Search query must be at least 2 characters';
  } else if (query.length > 500) {
    errors.query = 'Search query must be less than 500 characters';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate pagination params
 */
export function validatePaginationParams(params) {
  const errors = {};
  
  if (params.page !== undefined) {
    const page = parseInt(params.page, 10);
    if (isNaN(page) || page < 1) {
      errors.page = 'Page must be a positive integer';
    }
  }
  
  if (params.limit !== undefined) {
    const limit = parseInt(params.limit, 10);
    if (isNaN(limit) || limit < 1 || limit > 100) {
      errors.limit = 'Limit must be between 1 and 100';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Sanitize string input
 */
export function sanitizeString(str) {
  if (typeof str !== 'string') return '';
  return str
    .trim()
    .replace(/[<>]/g, '')
    .substring(0, 10000);
}

/**
 * Validate password strength
 */
export function validatePassword(password) {
  const errors = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    strength: calculatePasswordStrength(password),
  };
}

/**
 * Calculate password strength (0-100)
 */
function calculatePasswordStrength(password) {
  let strength = 0;
  
  if (password.length >= 8) strength += 20;
  if (password.length >= 12) strength += 10;
  if (/[A-Z]/.test(password)) strength += 15;
  if (/[a-z]/.test(password)) strength += 15;
  if (/[0-9]/.test(password)) strength += 20;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 20;
  
  return Math.min(strength, 100);
}
