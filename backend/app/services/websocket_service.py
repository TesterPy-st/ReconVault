"""
WebSocket service for ReconVault intelligence system.

This module provides WebSocket connection management for
real-time updates and notifications.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

# Configure logging
logger = logging.getLogger("reconvault.services.websocket")


class ConnectionManager:
    """
    WebSocket connection manager for handling multiple client connections.

    Manages WebSocket connections, broadcasts messages, and handles
    connection lifecycle events.
    """

    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.connection_limit = 1000  # Maximum connections

    async def connect(
        self, websocket: WebSocket, connection_id: Optional[str] = None
    ) -> str:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_id: Optional connection ID

        Returns:
            str: Generated connection ID
        """
        await websocket.accept()

        # Generate connection ID if not provided
        if not connection_id:
            connection_id = (
                f"conn_{len(self.active_connections)}_{datetime.now().timestamp()}"
            )

        # Check connection limit
        if len(self.active_connections) >= self.connection_limit:
            await websocket.close(code=1013, reason="Connection limit reached")
            raise ConnectionRefusedError("Maximum connections reached")

        # Store connection
        self.active_connections[connection_id] = websocket

        # Store metadata
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "user_agent": getattr(websocket, "headers", {}).get(
                "user-agent", "Unknown"
            ),
            "client_ip": getattr(websocket, "client", {}).get("host", "Unknown"),
            "subscriptions": set(),
            "message_count": 0,
        }

        logger.info(
            f"WebSocket connected: {connection_id} from {self.connection_metadata[connection_id]['client_ip']}"
        )

        # Send welcome message
        await self.send_personal_message(
            connection_id,
            {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "WebSocket connection established successfully",
            },
        )

        return connection_id

    def disconnect(
        self, connection_id: str, reason: str = "Client disconnected"
    ) -> None:
        """
        Remove a WebSocket connection.

        Args:
            connection_id: Connection ID to disconnect
            reason: Disconnection reason
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]

            logger.info(f"WebSocket disconnected: {connection_id} - {reason}")

    async def send_personal_message(
        self, connection_id: str, message: Dict[str, Any]
    ) -> bool:
        """
        Send a message to a specific connection.

        Args:
            connection_id: Target connection ID
            message: Message to send

        Returns:
            bool: True if message sent successfully
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            logger.warning(
                f"Attempted to send message to non-existent connection: {connection_id}"
            )
            return False

        try:
            # Update last activity
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["last_activity"] = datetime.now(
                    timezone.utc
                )
                self.connection_metadata[connection_id]["message_count"] += 1

            # Send message
            message_str = json.dumps(message, default=str)
            await websocket.send_text(message_str)
            return True

        except Exception as e:
            logger.error(f"Failed to send personal message to {connection_id}: {e}")
            # Connection might be broken, remove it
            self.disconnect(connection_id, f"Send failed: {e}")
            return False

    async def broadcast(
        self, message: Dict[str, Any], exclude_connection_ids: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast a message to all active connections.

        Args:
            message: Message to broadcast
            exclude_connection_ids: Connection IDs to exclude

        Returns:
            int: Number of messages sent successfully
        """
        if exclude_connection_ids is None:
            exclude_connection_ids = set()

        sent_count = 0
        failed_connections = []

        # Create message once
        message_str = json.dumps(message, default=str)

        for connection_id, websocket in list(self.active_connections.items()):
            if connection_id in exclude_connection_ids:
                continue

            try:
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id][
                        "last_activity"
                    ] = datetime.now(timezone.utc)
                    self.connection_metadata[connection_id]["message_count"] += 1

                await websocket.send_text(message_str)
                sent_count += 1

            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                failed_connections.append(connection_id)

        # Clean up failed connections
        for connection_id in failed_connections:
            self.disconnect(connection_id, f"Broadcast failed: {e}")

        return sent_count

    async def send_to_connections(
        self, connection_ids: List[str], message: Dict[str, Any]
    ) -> int:
        """
        Send a message to specific connections.

        Args:
            connection_ids: List of target connection IDs
            message: Message to send

        Returns:
            int: Number of messages sent successfully
        """
        sent_count = 0

        for connection_id in connection_ids:
            if await self.send_personal_message(connection_id, message):
                sent_count += 1

        return sent_count

    def get_active_connections_count(self) -> int:
        """
        Get number of active connections.

        Returns:
            int: Number of active connections
        """
        return len(self.active_connections)

    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get connection metadata.

        Args:
            connection_id: Connection ID

        Returns:
            Optional[Dict[str, Any]]: Connection metadata or None
        """
        return self.connection_metadata.get(connection_id)

    def get_all_connections_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all connections.

        Returns:
            Dict[str, Dict[str, Any]]: Connection information
        """
        return dict(self.connection_metadata)

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.

        Returns:
            Dict[str, Any]: Connection statistics
        """
        total_messages = sum(
            metadata.get("message_count", 0)
            for metadata in self.connection_metadata.values()
        )

        avg_messages = (
            total_messages / len(self.connection_metadata)
            if self.connection_metadata
            else 0
        )

        return {
            "total_connections": len(self.active_connections),
            "total_messages_sent": total_messages,
            "average_messages_per_connection": avg_messages,
            "connection_limit": self.connection_limit,
            "connection_usage_percent": (
                len(self.active_connections) / self.connection_limit
            )
            * 100,
        }

    def cleanup_inactive_connections(self, max_inactive_minutes: int = 30) -> int:
        """
        Clean up inactive connections.

        Args:
            max_inactive_minutes: Maximum inactive time in minutes

        Returns:
            int: Number of connections cleaned up
        """
        cutoff_time = datetime.now(timezone.utc)

        cleaned_count = 0
        inactive_connections = []

        for connection_id, metadata in self.connection_metadata.items():
            last_activity = metadata.get("last_activity")
            if last_activity:
                inactive_duration = (cutoff_time - last_activity).total_seconds() / 60
                if inactive_duration > max_inactive_minutes:
                    inactive_connections.append(connection_id)

        # Close inactive connections
        for connection_id in inactive_connections:
            self.disconnect(connection_id, "Inactive timeout")
            cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} inactive connections")

        return cleaned_count


class WebSocketService:
    """
    WebSocket service for handling intelligence system updates.

    Provides methods for sending real-time updates about targets,
    entities, intelligence findings, and system events.
    """

    def __init__(self):
        """Initialize WebSocket service"""
        self.connection_manager = ConnectionManager()
        self.notification_handlers = {}

        logger.info("WebSocket service initialized")

    async def handle_connection(
        self, websocket: WebSocket, connection_id: Optional[str] = None
    ) -> str:
        """
        Handle a new WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_id: Optional connection ID

        Returns:
            str: Connection ID
        """
        try:
            return await self.connection_manager.connect(websocket, connection_id)
        except Exception as e:
            logger.error(f"Failed to handle WebSocket connection: {e}")
            await websocket.close(code=1011, reason="Internal server error")
            raise

    async def handle_disconnection(self, connection_id: str) -> None:
        """
        Handle WebSocket disconnection.

        Args:
            connection_id: Disconnected connection ID
        """
        self.connection_manager.disconnect(connection_id, "Client disconnected")

    async def broadcast_target_update(
        self, target_data: Dict[str, Any], event_type: str = "target_updated"
    ) -> int:
        """
        Broadcast target update to all connected clients.

        Args:
            target_data: Target data
            event_type: Type of event

        Returns:
            int: Number of clients notified
        """
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": target_data,
        }

        return await self.connection_manager.broadcast(message)

    async def broadcast_entity_update(
        self, entity_data: Dict[str, Any], event_type: str = "entity_updated"
    ) -> int:
        """
        Broadcast entity update to all connected clients.

        Args:
            entity_data: Entity data
            event_type: Type of event

        Returns:
            int: Number of clients notified
        """
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": entity_data,
        }

        return await self.connection_manager.broadcast(message)

    async def broadcast_intelligence_update(
        self,
        intelligence_data: Dict[str, Any],
        event_type: str = "intelligence_updated",
    ) -> int:
        """
        Broadcast intelligence update to all connected clients.

        Args:
            intelligence_data: Intelligence data
            event_type: Type of event

        Returns:
            int: Number of clients notified
        """
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": intelligence_data,
        }

        return await self.connection_manager.broadcast(message)

    async def broadcast_graph_update(
        self, graph_data: Dict[str, Any], event_type: str = "graph_updated"
    ) -> int:
        """
        Broadcast graph update to all connected clients.

        Args:
            graph_data: Graph data
            event_type: Type of event

        Returns:
            int: Number of clients notified
        """
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": graph_data,
        }

        return await self.connection_manager.broadcast(message)

    async def broadcast_system_alert(
        self, alert_data: Dict[str, Any], severity: str = "info"
    ) -> int:
        """
        Broadcast system alert to all connected clients.

        Args:
            alert_data: Alert data
            severity: Alert severity level

        Returns:
            int: Number of clients notified
        """
        message = {
            "type": "system_alert",
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": alert_data,
        }

        return await self.connection_manager.broadcast(message)

    async def send_personal_notification(
        self, connection_id: str, notification_data: Dict[str, Any]
    ) -> bool:
        """
        Send personal notification to specific client.

        Args:
            connection_id: Target connection ID
            notification_data: Notification data

        Returns:
            bool: True if sent successfully
        """
        message = {
            "type": "personal_notification",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": notification_data,
        }

        return await self.connection_manager.send_personal_message(
            connection_id, message
        )

    async def send_heartbeat(self, connection_id: str) -> bool:
        """
        Send heartbeat to specific connection.

        Args:
            connection_id: Target connection ID

        Returns:
            bool: True if sent successfully
        """
        message = {
            "type": "heartbeat",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Server heartbeat",
        }

        return await self.connection_manager.send_personal_message(
            connection_id, message
        )

    async def broadcast_heartbeat_all(self) -> int:
        """
        Broadcast heartbeat to all connections.

        Returns:
            int: Number of heartbeats sent
        """
        message = {
            "type": "heartbeat",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Server heartbeat",
        }

        return await self.connection_manager.broadcast(message)

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket connection statistics.

        Returns:
            Dict[str, Any]: Connection statistics
        """
        return self.connection_manager.get_connection_stats()

    def get_active_connections_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active connections.

        Returns:
            Dict[str, Dict[str, Any]]: Connection information
        """
        return self.connection_manager.get_all_connections_info()

    def cleanup_inactive_connections(self, max_inactive_minutes: int = 30) -> int:
        """
        Clean up inactive connections.

        Args:
            max_inactive_minutes: Maximum inactive time in minutes

        Returns:
            int: Number of connections cleaned up
        """
        return self.connection_manager.cleanup_inactive_connections(
            max_inactive_minutes
        )

    async def start_background_tasks(self) -> None:
        """
        Start background tasks for WebSocket service.
        """
        # Start heartbeat task
        asyncio.create_task(self._heartbeat_task())

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

        logger.info("WebSocket background tasks started")

    async def _heartbeat_task(self) -> None:
        """Background task to send periodic heartbeats"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                await self.broadcast_heartbeat_all()
            except Exception as e:
                logger.error(f"Heartbeat task error: {e}")

    async def _cleanup_task(self) -> None:
        """Background task to clean up inactive connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                self.cleanup_inactive_connections()
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")


# Global WebSocket service instance
websocket_service = WebSocketService()


def get_websocket_service() -> WebSocketService:
    """
    Get global WebSocket service instance.

    Returns:
        WebSocketService: Global WebSocket service
    """
    return websocket_service
