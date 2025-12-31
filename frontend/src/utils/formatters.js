// ReconVault Data Formatting Functions

import { RISK_LEVELS, TARGET_STATUS, DATE_FORMATS } from './constants';

/**
 * Format date for display
 */
export function formatDate(date, format = DATE_FORMATS.DISPLAY) {
  if (!date) return '';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];
  
  const padZero = (num) => num.toString().padStart(2, '0');
  
  const replacements = {
    'MMM': months[d.getMonth()],
    'yyyy': d.getFullYear(),
    'yy': d.getFullYear().toString().slice(-2),
    'MM': padZero(d.getMonth() + 1),
    'dd': padZero(d.getDate()),
    'HH': padZero(d.getHours()),
    'mm': padZero(d.getMinutes()),
    'ss': padZero(d.getSeconds()),
    'SSS': d.getMilliseconds().toString().padStart(3, '0'),
  };
  
  let formatted = format;
  Object.entries(replacements).forEach(([key, value]) => {
    formatted = formatted.replace(key, value);
  });
  
  return formatted;
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  if (!date) return '';
  
  const now = new Date();
  const d = new Date(date);
  const diffMs = now - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  const diffWeek = Math.floor(diffDay / 7);
  const diffMonth = Math.floor(diffDay / 30);
  const diffYear = Math.floor(diffDay / 365);
  
  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  if (diffWeek < 4) return `${diffWeek} week${diffWeek > 1 ? 's' : ''} ago`;
  if (diffMonth < 12) return `${diffMonth} month${diffMonth > 1 ? 's' : ''} ago`;
  return `${diffYear} year${diffYear > 1 ? 's' : ''} ago`;
}

/**
 * Format status with label and color
 */
export function formatStatus(status) {
  const statusConfig = {
    [TARGET_STATUS.PENDING]: { label: 'Pending', color: 'yellow' },
    [TARGET_STATUS.QUEUED]: { label: 'Queued', color: 'blue' },
    [TARGET_STATUS.PROCESSING]: { label: 'Processing', color: 'purple' },
    [TARGET_STATUS.COMPLETED]: { label: 'Completed', color: 'green' },
    [TARGET_STATUS.FAILED]: { label: 'Failed', color: 'red' },
    [TARGET_STATUS.CANCELLED]: { label: 'Cancelled', color: 'gray' },
  };
  
  return statusConfig[status] || { label: status, color: 'gray' };
}

/**
 * Format risk level with label and color
 */
export function formatRiskLevel(score) {
  let level;
  let color;
  
  if (score >= 80) {
    level = RISK_LEVELS.CRITICAL;
    color = '#ff006e';
  } else if (score >= 60) {
    level = RISK_LEVELS.HIGH;
    color = '#ff6600';
  } else if (score >= 40) {
    level = RISK_LEVELS.MEDIUM;
    color = '#ffcc00';
  } else {
    level = RISK_LEVELS.LOW;
    color = '#00ff88';
  }
  
  return { level, color, label: capitalize(level) };
}

/**
 * Format number with commas
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0';
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined) return '0%';
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${units[i]}`;
}

/**
 * Format duration in milliseconds to human readable string
 */
export function formatDuration(ms) {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  if (ms < 86400000) return `${(ms / 3600000).toFixed(1)}h`;
  return `${(ms / 86400000).toFixed(1)}d`;
}

/**
 * Format IP address for display
 */
export function formatIpAddress(ip) {
  if (!ip) return '';
  return ip;
}

/**
 * Format domain for display
 */
export function formatDomain(domain) {
  if (!domain) return '';
  return domain.toLowerCase();
}

/**
 * Format email for display
 */
export function formatEmail(email) {
  if (!email) return '';
  return email.toLowerCase();
}

/**
 * Format phone number for display
 */
export function formatPhone(phone) {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned.startsWith('1')) {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  return phone;
}

/**
 * Format ASN number
 */
export function formatAsn(asn) {
  if (!asn) return '';
  return `AS${asn}`;
}

/**
 * Format location (city, country)
 */
export function formatLocation(city, country) {
  if (!city && !country) return 'Unknown';
  if (!city) return country;
  if (!country) return city;
  return `${city}, ${country}`;
}

/**
 * Format array to comma-separated string
 */
export function formatArray(arr, maxItems = 3) {
  if (!Array.isArray(arr) || arr.length === 0) return 'None';
  if (arr.length <= maxItems) return arr.join(', ');
  return `${arr.slice(0, maxItems).join(', ')} +${arr.length - maxItems} more`;
}

/**
 * Format object to key-value string
 */
export function formatKeyValue(obj, separator = ': ') {
  if (!obj || typeof obj !== 'object') return '';
  return Object.entries(obj)
    .map(([key, value]) => `${key}${separator}${value}`)
    .join('\n');
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format JSON for display
 */
export function formatJSON(data, indent = 2) {
  if (!data) return '';
  return JSON.stringify(data, null, indent);
}

/**
 * Format UUID to shortened version
 */
export function formatUuid(uuid) {
  if (!uuid) return '';
  return `${uuid.substring(0, 8)}...${uuid.substring(uuid.length - 8)}`;
}

/**
 * Format currency
 */
export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

/**
 * Format number with suffix (K, M, B)
 */
export function formatCompactNumber(num) {
  if (num === null || num === undefined) return '0';
  
  const suffixes = ['', 'K', 'M', 'B', 'T'];
  const suffixNum = Math.floor(''.length / 3);
  
  if (suffixNum >= suffixes.length) return num.toString();
  
  const shortValue = parseFloat((num / Math.pow(1000, suffixNum)).toPrecision(3));
  if (shortValue % 1 !== 0) {
    return shortValue.toFixed(1) + suffixes[suffixNum];
  }
  return shortValue.toString() + suffixes[suffixNum];
}
