// ReconVault WebSocket Service

import { WS_BASE_URL } from '../utils/constants';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.isConnected = false;
    this.messageQueue = [];
  }

  connect(path = '/ws') {
    const wsUrl = WS_BASE_URL + path;
    console.log(`[WS] Connecting to ${wsUrl}...`);

    try {
      this.socket = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.handleReconnect();
    }
  }

  setupEventHandlers() {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('[WS] Connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.processMessageQueue();
      this.emit('connection', { status: 'connected' });
    };

    this.socket.onclose = (event) => {
      console.log('[WS] Disconnected:', event.code, event.reason);
      this.isConnected = false;
      this.emit('connection', { status: 'disconnected', code: event.code });
      
      if (!event.wasClean) {
        this.handleReconnect();
      }
    };

    this.socket.onerror = (error) => {
      console.error('[WS] Error:', error);
      this.emit('error', error);
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('[WS] Failed to parse message:', error);
      }
    };
  }

  handleMessage(data) {
    const { type, payload } = data;

    switch (type) {
      case 'entity_discovered':
        this.emit('entity:discovered', payload);
        break;
      case 'entity_updated':
        this.emit('entity:updated', payload);
        break;
      case 'relationship_found':
        this.emit('relationship:found', payload);
        break;
      case 'intelligence_found':
        this.emit('intelligence:found', payload);
        break;
      case 'target_status_update':
        this.emit('target:status', payload);
        break;
      case 'risk_score_update':
        this.emit('risk:score', payload);
        break;
      case 'recon_progress':
        this.emit('recon:progress', payload);
        break;
      case 'recon_complete':
        this.emit('recon:complete', payload);
        break;
      case 'recon_error':
        this.emit('recon:error', payload);
        break;
      case 'graph_update':
        this.emit('graph:update', payload);
        break;
      case 'notification':
        this.emit('notification', payload);
        break;
      case 'pong':
        this.emit('pong', payload);
        break;
      default:
        this.emit('message', data);
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      this.emit('connection', { status: 'failed' });
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message.type, message.payload);
    }
  }

  send(type, payload = {}) {
    const message = JSON.stringify({ type, payload });
    
    if (this.isConnected && this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(message);
    } else {
      console.warn('[WS] Cannot send message, queuing...');
      this.messageQueue.push({ type, payload });
    }
  }

  ping() {
    this.send('ping', { timestamp: Date.now() });
  }

  subscribe(channel, entityId = null) {
    this.send('subscribe', { channel, entity_id: entityId });
  }

  unsubscribe(channel, entityId = null) {
    this.send('unsubscribe', { channel, entity_id: entityId });
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`[WS] Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close(1000, 'Client disconnect');
      this.socket = null;
    }
    this.isConnected = false;
    this.listeners.clear();
    this.messageQueue = [];
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      readyState: this.socket?.readyState,
      reconnectAttempts: this.reconnectAttempts,
    };
  }
}

// Singleton instance
const wsService = new WebSocketService();

export default wsService;

// WebSocket event types
export const WS_EVENTS = {
  CONNECTION: 'connection',
  ENTITY_DISCOVERED: 'entity:discovered',
  ENTITY_UPDATED: 'entity:updated',
  RELATIONSHIP_FOUND: 'relationship:found',
  INTELLIGENCE_FOUND: 'intelligence:found',
  TARGET_STATUS: 'target:status',
  RISK_SCORE: 'risk:score',
  RECON_PROGRESS: 'recon:progress',
  RECON_COMPLETE: 'recon:complete',
  RECON_ERROR: 'recon:error',
  GRAPH_UPDATE: 'graph:update',
  NOTIFICATION: 'notification',
  MESSAGE: 'message',
};

// WebSocket channels
export const WS_CHANNELS = {
  TARGETS: 'targets',
  ENTITIES: 'entities',
  GRAPH: 'graph',
  INTELLIGENCE: 'intelligence',
  NOTIFICATIONS: 'notifications',
};
