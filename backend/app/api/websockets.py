"""
WebSocket endpoints for ReconVault API.

This module provides WebSocket endpoints for real-time
updates and notifications.
"""

import logging
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_service import get_websocket_service

# Configure logging
logger = logging.getLogger("reconvault.api.websocket")

# Create router
router = APIRouter()


@router.websocket("/intelligence")
async def websocket_intelligence_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for intelligence updates.

    This endpoint provides real-time updates about:
    - Target updates
    - Entity discoveries
    - Intelligence findings
    - Graph changes
    - System alerts
    """
    websocket_service = get_websocket_service()
    connection_id = None

    try:
        # Accept connection
        connection_id = await websocket_service.handle_connection(websocket)

        logger.info(f"WebSocket intelligence connection established: {connection_id}")

        # Send initial connection info
        await websocket.send_json(
            {
                "type": "connection_info",
                "connection_id": connection_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Intelligence WebSocket connected",
            }
        )

        # Handle messages from client
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                # Process client message
                message_type = data.get("type")

                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})

                elif message_type == "subscribe":
                    # Handle subscription to specific updates
                    subscription_type = data.get("subscription_type")
                    logger.info(f"Client {connection_id} subscribed to: {subscription_type}")

                    await websocket.send_json(
                        {
                            "type": "subscription_confirmed",
                            "subscription_type": subscription_type,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                elif message_type == "unsubscribe":
                    # Handle unsubscription
                    subscription_type = data.get("subscription_type")
                    logger.info(f"Client {connection_id} unsubscribed from: {subscription_type}")

                    await websocket.send_json(
                        {
                            "type": "unsubscription_confirmed",
                            "subscription_type": subscription_type,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                elif message_type == "get_stats":
                    # Send connection statistics
                    stats = websocket_service.get_connection_stats()
                    await websocket.send_json(
                        {
                            "type": "connection_stats",
                            "stats": stats,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                else:
                    # Unknown message type
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": f"Unknown message type: {message_type}",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error for {connection_id}: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": f"Message handling error: {str(e)}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if connection_id:
            await websocket_service.handle_disconnection(connection_id)
    finally:
        # Ensure connection is cleaned up
        if connection_id:
            await websocket_service.handle_disconnection(connection_id)


@router.websocket("/notifications")
async def websocket_notifications_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for system notifications.

    This endpoint provides system-wide notifications:
    - Security alerts
    - System status changes
    - Critical updates
    """
    websocket_service = get_websocket_service()
    connection_id = None

    try:
        # Accept connection
        connection_id = await websocket_service.handle_connection(websocket)

        logger.info(f"WebSocket notifications connection established: {connection_id}")

        # Send welcome message
        await websocket.send_json(
            {
                "type": "notifications_connected",
                "connection_id": connection_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Notifications WebSocket connected",
            }
        )

        # Handle messages from client
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                elif message_type == "get_notifications":
                    # In a real implementation, this would fetch recent notifications
                    await websocket.send_json(
                        {
                            "type": "notifications",
                            "notifications": [],
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket notifications client disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket notifications error for {connection_id}: {e}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket notifications connection closed: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket notifications connection error: {e}")
    finally:
        if connection_id:
            await websocket_service.handle_disconnection(connection_id)


@router.websocket("/monitoring")
async def websocket_monitoring_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for system monitoring updates.

    This endpoint provides real-time monitoring data:
    - System health metrics
    - Performance statistics
    - Connection status
    """
    websocket_service = get_websocket_service()
    connection_id = None

    try:
        # Accept connection
        connection_id = await websocket_service.handle_connection(websocket)

        logger.info(f"WebSocket monitoring connection established: {connection_id}")

        # Send initial monitoring data
        stats = websocket_service.get_connection_stats()
        await websocket.send_json(
            {
                "type": "monitoring_data",
                "connection_stats": stats,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Handle messages from client
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                elif message_type == "get_monitoring":
                    # Send updated monitoring data
                    stats = websocket_service.get_connection_stats()
                    await websocket.send_json(
                        {
                            "type": "monitoring_data",
                            "connection_stats": stats,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            except WebSocketDisconnect:
                logger.info(f"WebSocket monitoring client disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket monitoring error for {connection_id}: {e}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket monitoring connection closed: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket monitoring connection error: {e}")
    finally:
        if connection_id:
            await websocket_service.handle_disconnection(connection_id)


# Helper function to broadcast updates from other parts of the system
async def broadcast_intelligence_update(data: Dict, event_type: str = "intelligence_updated"):
    """
    Broadcast intelligence update to all connected WebSocket clients.

    Args:
        data: Data to broadcast
        event_type: Type of event
    """
    websocket_service = get_websocket_service()

    message = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }

    return await websocket_service.connection_manager.broadcast(message)


async def broadcast_system_alert(alert_data: Dict, severity: str = "info"):
    """
    Broadcast system alert to all connected WebSocket clients.

    Args:
        alert_data: Alert data
        severity: Alert severity
    """
    websocket_service = get_websocket_service()

    return await websocket_service.broadcast_system_alert(alert_data, severity)


async def broadcast_target_update(target_data: Dict):
    """
    Broadcast target update to all connected WebSocket clients.

    Args:
        target_data: Target data
    """
    websocket_service = get_websocket_service()

    return await websocket_service.broadcast_target_update(target_data)


async def broadcast_entity_update(entity_data: Dict):
    """
    Broadcast entity update to all connected WebSocket clients.

    Args:
        entity_data: Entity data
    """
    websocket_service = get_websocket_service()

    return await websocket_service.broadcast_entity_update(entity_data)


async def broadcast_compliance_violation(violation_data: Dict):
    """
    Broadcast compliance violation to all connected WebSocket clients.

    Args:
        violation_data: Violation data
    """
    websocket_service = get_websocket_service()

    message = {
        "type": "compliance_violation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": violation_data,
    }

    return await websocket_service.connection_manager.broadcast(message)


# Export broadcast functions for use in other modules
__all__ = [
    "broadcast_intelligence_update",
    "broadcast_system_alert",
    "broadcast_target_update",
    "broadcast_entity_update",
    "broadcast_compliance_violation",
]
