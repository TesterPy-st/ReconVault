"""
WebSocket Manager for ReconVault intelligence system.

This module provides advanced WebSocket management capabilities including
message broadcasting, connection pooling, rate limiting, and message queuing.
"""

import asyncio
import gzip
import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from app.services.websocket_service import WebSocketService

# Configure logging
logger = logging.getLogger("reconvault.services.websocket_manager")


class MessageType(Enum):
    """WebSocket message types"""
    GRAPH_NODE_ADDED = "graph:node:added"
    GRAPH_NODE_UPDATED = "graph:node:updated"
    GRAPH_EDGE_ADDED = "graph:edge:added"
    GRAPH_BATCH_UPDATE = "graph:batch:update"
    COLLECTION_STARTED = "collection:started"
    COLLECTION_PROGRESS = "collection:progress"
    COLLECTION_COMPLETED = "collection:completed"
    COLLECTION_ERROR = "collection:error"
    METRICS_GRAPH_UPDATE = "metrics:graph:update"
    METRICS_RISK_UPDATE = "metrics:risk:update"
    METRICS_ANOMALY_DETECTED = "metrics:anomaly:detected"
    NOTIFICATION_ALERT = "notification:alert"


class WebSocketManager:
    """
    Advanced WebSocket manager with broadcasting, batching, and rate limiting.
    
    Features:
    - Broadcast to all or specific users
    - Message batching for efficiency
    - Rate limiting per client
    - Message queuing for offline clients
    - Automatic cleanup of stale connections
    - Message compression
    """

    def __init__(self, websocket_service: Optional[WebSocketService] = None):
        """Initialize WebSocket manager"""
        from app.services.websocket_service import get_websocket_service
        self.websocket_service = websocket_service or get_websocket_service()
        
        # Message batching
        self.batch_queue = defaultdict(list)
        self.batch_timer = None
        self.batch_interval_ms = 100  # Batch messages every 100ms
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: {"count": 0, "reset_time": None})
        self.rate_limit_max = 100  # Max 100 messages per second per client
        self.rate_limit_window = 1.0  # 1 second window
        
        # Message queuing for offline clients
        self.message_queues = defaultdict(lambda: deque(maxlen=1000))  # Store up to 1000 messages
        
        # Metrics
        self.message_count = 0
        self.broadcast_count = 0
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("WebSocket manager initialized")

    async def broadcast_to_all(
        self,
        message: Dict[str, Any],
        exclude: Optional[Set[str]] = None,
        compress: bool = True
    ) -> int:
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
            exclude: Set of connection IDs to exclude
            compress: Whether to compress the message
        
        Returns:
            int: Number of clients notified
        """
        try:
            self.message_count += 1
            self.broadcast_count += 1
            
            # Prepare message
            prepared_message = self._prepare_message(message, compress)
            
            # Broadcast
            sent_count = await self.websocket_service.connection_manager.broadcast(
                prepared_message,
                exclude_connection_ids=exclude
            )
            
            logger.debug(f"Broadcast to {sent_count} clients: {message.get('type')}")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to broadcast to all: {e}")
            return 0

    async def broadcast_to_user(
        self,
        user_id: str,
        message: Dict[str, Any],
        compress: bool = True
    ) -> int:
        """
        Broadcast message to specific user's connections.
        
        Args:
            user_id: User ID
            message: Message to broadcast
            compress: Whether to compress the message
        
        Returns:
            int: Number of clients notified
        """
        try:
            self.message_count += 1
            
            # Find user's connections (in a real implementation, this would query user connection mappings)
            connections_info = self.websocket_service.get_active_connections_info()
            user_connections = [
                conn_id for conn_id, metadata in connections_info.items()
                if metadata.get("user_id") == user_id
            ]
            
            if not user_connections:
                # Queue message for user when they come online
                self.message_queues[user_id].append(message)
                logger.debug(f"Queued message for offline user {user_id}")
                return 0
            
            # Prepare message
            prepared_message = self._prepare_message(message, compress)
            
            # Send to user's connections
            sent_count = 0
            for conn_id in user_connections:
                if await self._check_rate_limit(conn_id):
                    if await self.websocket_service.connection_manager.send_personal_message(
                        conn_id, prepared_message
                    ):
                        sent_count += 1
            
            logger.debug(f"Broadcast to user {user_id}: {sent_count} clients")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to broadcast to user {user_id}: {e}")
            return 0

    async def broadcast_graph_update(
        self,
        node_or_edge: Dict[str, Any],
        operation: str,
        batch: bool = False
    ) -> int:
        """
        Broadcast graph update to all clients.
        
        Args:
            node_or_edge: Node or edge data
            operation: Operation type (add, update, delete)
            batch: Whether to batch this update
        
        Returns:
            int: Number of clients notified
        """
        try:
            # Determine message type
            if operation == "add":
                if "source" in node_or_edge or "source_id" in node_or_edge:
                    message_type = MessageType.GRAPH_EDGE_ADDED
                    message = {
                        "type": message_type.value,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "source_id": node_or_edge.get("source") or node_or_edge.get("source_id"),
                            "target_id": node_or_edge.get("target") or node_or_edge.get("target_id"),
                            "relationship_type": node_or_edge.get("relationship_type"),
                            "confidence": node_or_edge.get("confidence", 1.0)
                        }
                    }
                else:
                    message_type = MessageType.GRAPH_NODE_ADDED
                    message = {
                        "type": message_type.value,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": {
                            "node_id": node_or_edge.get("id"),
                            "node_type": node_or_edge.get("type") or node_or_edge.get("entity_type"),
                            "properties": node_or_edge.get("properties", node_or_edge)
                        }
                    }
            elif operation == "update":
                message_type = MessageType.GRAPH_NODE_UPDATED
                message = {
                    "type": message_type.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "node_id": node_or_edge.get("id"),
                        "changed_fields": node_or_edge.get("changed_fields", {}),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            else:
                logger.warning(f"Unknown graph operation: {operation}")
                return 0
            
            if batch:
                # Add to batch queue
                batch_type = "edges" if "edge" in message_type.value else "nodes"
                self.batch_queue[batch_type].append(message["data"])
                return 0
            else:
                # Broadcast immediately
                return await self.broadcast_to_all(message)
                
        except Exception as e:
            logger.error(f"Failed to broadcast graph update: {e}")
            return 0

    async def broadcast_batch_update(
        self,
        nodes_added: List[Dict[str, Any]] = None,
        edges_added: List[Dict[str, Any]] = None,
        nodes_updated: List[Dict[str, Any]] = None
    ) -> int:
        """
        Broadcast batch graph updates to all clients.
        
        Args:
            nodes_added: List of added nodes
            edges_added: List of added edges
            nodes_updated: List of updated nodes
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.GRAPH_BATCH_UPDATE.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "nodes_added": nodes_added or [],
                    "edges_added": edges_added or [],
                    "nodes_updated": nodes_updated or []
                }
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast batch update: {e}")
            return 0

    async def broadcast_collection_progress(
        self,
        collection_id: str,
        data: Dict[str, Any]
    ) -> int:
        """
        Broadcast collection progress update to all clients.
        
        Args:
            collection_id: Collection task ID
            data: Progress data
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.COLLECTION_PROGRESS.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "collection_id": collection_id,
                    "entities_found": data.get("entities_found", 0),
                    "relationships_found": data.get("relationships_found", 0),
                    "status": data.get("status", "running"),
                    "percentage": data.get("percentage", 0)
                }
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast collection progress: {e}")
            return 0

    async def broadcast_collection_started(
        self,
        collection_id: str,
        target: str,
        collector_type: str
    ) -> int:
        """
        Broadcast collection started event.
        
        Args:
            collection_id: Collection task ID
            target: Target being collected
            collector_type: Type of collector
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.COLLECTION_STARTED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "collection_id": collection_id,
                    "target": target,
                    "collector_type": collector_type
                }
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast collection started: {e}")
            return 0

    async def broadcast_collection_completed(
        self,
        collection_id: str,
        total_entities: int,
        total_relationships: int,
        duration: float
    ) -> int:
        """
        Broadcast collection completed event.
        
        Args:
            collection_id: Collection task ID
            total_entities: Total entities collected
            total_relationships: Total relationships collected
            duration: Duration in seconds
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.COLLECTION_COMPLETED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "collection_id": collection_id,
                    "total_entities": total_entities,
                    "total_relationships": total_relationships,
                    "duration": duration
                }
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast collection completed: {e}")
            return 0

    async def broadcast_collection_error(
        self,
        collection_id: str,
        error_message: str,
        error_type: str
    ) -> int:
        """
        Broadcast collection error event.
        
        Args:
            collection_id: Collection task ID
            error_message: Error message
            error_type: Type of error
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.COLLECTION_ERROR.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "collection_id": collection_id,
                    "error_message": error_message,
                    "error_type": error_type
                }
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast collection error: {e}")
            return 0

    async def broadcast_metrics(
        self,
        metrics_data: Dict[str, Any],
        metrics_type: str = "graph"
    ) -> int:
        """
        Broadcast metrics update to all clients.
        
        Args:
            metrics_data: Metrics data
            metrics_type: Type of metrics (graph, risk, anomaly)
        
        Returns:
            int: Number of clients notified
        """
        try:
            if metrics_type == "graph":
                message_type = MessageType.METRICS_GRAPH_UPDATE
            elif metrics_type == "risk":
                message_type = MessageType.METRICS_RISK_UPDATE
            elif metrics_type == "anomaly":
                message_type = MessageType.METRICS_ANOMALY_DETECTED
            else:
                logger.warning(f"Unknown metrics type: {metrics_type}")
                return 0
            
            message = {
                "type": message_type.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": metrics_data
            }
            
            return await self.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast metrics: {e}")
            return 0

    async def broadcast_alert(
        self,
        message: str,
        alert_type: str = "info",
        severity: str = "info"
    ) -> int:
        """
        Broadcast alert notification to all clients.
        
        Args:
            message: Alert message
            alert_type: Type of alert
            severity: Severity level (info, warning, error, critical)
        
        Returns:
            int: Number of clients notified
        """
        try:
            message = {
                "type": MessageType.NOTIFICATION_ALERT.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "message": message,
                    "type": alert_type,
                    "severity": severity
                }
            }
            
            return await self.broadcast_to_all(message, compress=False)  # Don't compress alerts
            
        except Exception as e:
            logger.error(f"Failed to broadcast alert: {e}")
            return 0

    def get_active_connections_count(self) -> int:
        """
        Get number of active connections.
        
        Returns:
            int: Number of active connections
        """
        return self.websocket_service.connection_manager.get_active_connections_count()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get WebSocket manager statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_messages": self.message_count,
            "total_broadcasts": self.broadcast_count,
            "active_connections": self.get_active_connections_count(),
            "queued_messages": sum(len(q) for q in self.message_queues.values()),
            "batch_queue_size": len(self.batch_queue["nodes"]) + len(self.batch_queue["edges"]),
            "messages_per_second": self.message_count / uptime if uptime > 0 else 0
        }

    async def process_batch_queue(self) -> int:
        """
        Process accumulated batch messages.
        
        Returns:
            int: Number of clients notified
        """
        try:
            if not self.batch_queue["nodes"] and not self.batch_queue["edges"]:
                return 0
            
            sent_count = await self.broadcast_batch_update(
                nodes_added=self.batch_queue["nodes"],
                edges_added=self.batch_queue["edges"]
            )
            
            # Clear batch queues
            self.batch_queue["nodes"].clear()
            self.batch_queue["edges"].clear()
            
            logger.debug(f"Processed batch update: {sent_count} clients notified")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to process batch queue: {e}")
            return 0

    async def start_batch_processor(self) -> None:
        """Start background batch processor"""
        while True:
            try:
                await asyncio.sleep(self.batch_interval_ms / 1000)
                await self.process_batch_queue()
            except Exception as e:
                logger.error(f"Batch processor error: {e}")

    def _prepare_message(self, message: Dict[str, Any], compress: bool) -> Dict[str, Any]:
        """
        Prepare message for sending.
        
        Args:
            message: Message to prepare
            compress: Whether to compress the message
        
        Returns:
            Dict[str, Any]: Prepared message
        """
        prepared = message.copy()
        
        # Add timestamp if not present
        if "timestamp" not in prepared:
            prepared["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Compress message data if enabled and data is large
        if compress and "data" in prepared:
            data_str = json.dumps(prepared["data"])
            if len(data_str) > 1024:  # Only compress if > 1KB
                compressed = gzip.compress(data_str.encode())
                prepared["data"] = {
                    "_compressed": True,
                    "_encoding": "gzip",
                    "_data": compressed.hex()
                }
        
        return prepared

    async def _check_rate_limit(self, connection_id: str) -> bool:
        """
        Check if connection is within rate limit.
        
        Args:
            connection_id: Connection ID to check
        
        Returns:
            bool: True if within rate limit
        """
        now = datetime.now(timezone.utc).timestamp()
        rate_limit = self.rate_limits[connection_id]
        
        # Reset counter if time window passed
        if rate_limit["reset_time"] is None or now >= rate_limit["reset_time"]:
            rate_limit["count"] = 0
            rate_limit["reset_time"] = now + self.rate_limit_window
        
        # Check if over limit
        if rate_limit["count"] >= self.rate_limit_max:
            logger.warning(f"Rate limit exceeded for connection {connection_id}")
            return False
        
        rate_limit["count"] += 1
        return True


# Global WebSocket manager instance
_websocket_manager = None


def get_websocket_manager() -> WebSocketManager:
    """
    Get global WebSocket manager instance.
    
    Returns:
        WebSocketManager: Global WebSocket manager
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
        # Start batch processor in background
        asyncio.create_task(_websocket_manager.start_batch_processor())
    return _websocket_manager
