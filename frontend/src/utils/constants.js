// ReconVault Constants and Enums

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const TARGET_TYPES = {
  DOMAIN: 'domain',
  IP_ADDRESS: 'ip_address',
  EMAIL: 'email',
  PHONE: 'phone',
  SOCIAL_MEDIA: 'social_media',
  PERSON: 'person',
  ORGANIZATION: 'organization',
  KEYWORD: 'keyword',
  FILE: 'file',
  WIFI: 'wifi',
};

export const TARGET_STATUS = {
  PENDING: 'pending',
  QUEUED: 'queued',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
};

export const ENTITY_TYPES = {
  DOMAIN: 'domain',
  IP_ADDRESS: 'ip_address',
  EMAIL: 'email',
  PHONE: 'phone',
  PERSON: 'person',
  ORGANIZATION: 'organization',
  NETWORK: 'network',
  SERVICE: 'service',
  VULNERABILITY: 'vulnerability',
  FILE: 'file',
  SOCIAL_ACCOUNT: 'social_account',
  DEVICE: 'device',
  LOCATION: 'location',
};

export const RELATIONSHIP_TYPES = {
  OWNS: 'owns',
  HOSTS: 'hosts',
  RESOLVES_TO: 'resolves_to',
  ASSOCIATED_WITH: 'associated_with',
  LOCATED_AT: 'located_at',
  PART_OF: 'part_of',
  DEPENDS_ON: 'depends_on',
  COMMUNICATES_WITH: 'communicates_with',
  CONTAINS: 'contains',
  DERIVED_FROM: 'derived_from',
};

export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
};

export const RISK_COLORS = {
  low: '#00ff88',
  medium: '#ffcc00',
  high: '#ff6600',
  critical: '#ff006e',
};

export const INTELLIGENCE_SOURCES = {
  WHOIS: 'whois',
  DNS: 'dns',
  SSL: 'ssl',
  OSINT: 'osint',
  SOCIAL: 'social',
  VULNERABILITY: 'vulnerability',
  PASSIVE_DNS: 'passive_dns',
  SHODAN: 'shodan',
  CENSYS: 'censys',
  GOOGLE_DORKING: 'google_dorking',
};

export const PAGE_SIZE = 20;
export const GRAPH_NODE_SIZE = 10;
export const GRAPH_LINK_WIDTH = 2;
export const MAX_GRAPH_NODES = 500;

export const TOAST_DURATION = 5000;
export const TOAST_POSITIONS = {
  TOP_RIGHT: 'top-right',
  TOP_LEFT: 'top-left',
  BOTTOM_RIGHT: 'bottom-right',
  BOTTOM_LEFT: 'bottom-left',
};

export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy HH:mm',
  API: 'YYYY-MM-DDTHH:mm:ss.SSSZ',
  SHORT: 'MMM dd, yyyy',
};

export const STORAGE_KEYS = {
  THEME: 'reconvault_theme',
  USER_PREFERENCES: 'reconvault_preferences',
  AUTH_TOKEN: 'reconvault_token',
  RECENT_TARGETS: 'reconvault_recent_targets',
};

export const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: 'dashboard' },
  { path: '/graph', label: 'Graph', icon: 'graph' },
  { path: '/intelligence', label: 'Intelligence', icon: 'intelligence' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
  { path: '/about', label: 'About', icon: 'about' },
];
