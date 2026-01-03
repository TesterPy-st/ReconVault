"""
WebSocket endpoints for ReconVault API.

This module provides WebSocket endpoints for real-time
updates and notifications.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import logging
from datetime import datetime, timezone
import asyncio

from app.services.websocket_service import get_websocket_service
from app.services.websocket_manager import (
    get_websocket_manager,
    MessageType
)

# Configure logging
logger = logging.getLogger("reconvault.api.websocket")

# Create router
router = APIRouter()

# Message throttling
last_metrics_broadcast = {}
METRICS_THROTTLE_SECONDS = 1  # Throttle metrics to 1Hz


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
        await websocket.send_json({
            "type": "connection_info",
            "connection_id": connection_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Intelligence WebSocket connected"
        })
        
        # Handle messages from client
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                # Process client message
                message_type = data.get("type")
                
                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                elif message_type == "subscribe":
                    # Handle subscription to specific updates
                    subscription_type = data.get("subscription_type")
                    logger.info(f"Client {connection_id} subscribed to: {subscription_type}")
                    
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "subscription_type": subscription_type,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                elif message_type == "unsubscribe":
                    # Handle unsubscription
                    subscription_type = data.get("subscription_type")
                    logger.info(f"Client {connection_id} unsubscribed from: {subscription_type}")
                    
                    await websocket.send_json({
                        "type": "unsubscription_confirmed",
                        "subscription_type": subscription_type,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                elif message_type == "get_stats":
                    # Send connection statistics
                    stats = websocket_service.get_connection_stats()
                    await websocket.send_json({
                        "type": "connection_stats",
                        "stats": stats,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected: {connection_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket message handling error for {connection_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": f"Message handling error: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
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
        await websocket.send_json({
            "type": "notifications_connected",
            "connection_id": connection_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Notifications WebSocket connected"
        })
        
        # Handle messages from client
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                elif message_type == "get_notifications":
                    # In a real implementation, this would fetch recent notifications
                    await websocket.send_json({
                        "type": "notifications",
                        "notifications": [],
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
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
        await websocket.send_json({
            "type": "monitoring_data",
            "connection_stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Handle messages from client
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                elif message_type == "get_monitoring":
                    # Send updated monitoring data
                    stats = websocket_service.get_connection_stats()
                    await websocket.send_json({
                        "type": "monitoring_data",
                        "connection_stats": stats,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
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
        "data": data
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


# Export broadcast functions for use in other modules
__all__ = [
    "broadcast_intelligence_update",
    "broadcast_system_alert", 
    "broadcast_target_update",
    "broadcast_entity_update",
    "broadcast_graph_node_added",
    "broadcast_graph_node_updated",
    "broadcast_graph_edge_added",
    "broadcast_graph_batch_update",
    "broadcast_collection_started",
    "broadcast_collection_progress",
    "broadcast_collection_completed",
    "broadcast_collection_error",
    "broadcast_graph_metrics",
    "broadcast_risk_metrics",
    "broadcast_anomaly_detected",
    "broadcast_notification_alert"
]


# Graph Update Broadcast Functions

async def broadcast_graph_node_added(node_data: Dict) -> int:
    """
    Broadcast node added event to all connected clients.
    
    Args:
        node_data: Node data including id, type, and properties
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_graph_update(node_data, operation="add")


async def broadcast_graph_node_updated(node_data: Dict) -> int:
    """
    Broadcast node updated event to all connected clients.
    
    Args:
        node_data: Node data including id and changed fields
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_graph_update(node_data, operation="update")


async def broadcast_graph_edge_added(edge_data: Dict) -> int:
    """
    Broadcast edge added event to all connected clients.
    
    Args:
        edge_data: Edge data including source, target, and relationship_type
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_graph_update(edge_data, operation="add")


async def broadcast_graph_batch_update(
    nodes_added: List[Dict] = None,
    edges_added: List[Dict] = None,
    nodes_updated: List[Dict] = None
) -> int:
    """
    Broadcast batch graph update to all connected clients.
    
    Args:
        nodes_added: List of added nodes
        edges_added: List of added edges
        nodes_updated: List of updated nodes
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_batch_update(nodes_added, edges_added, nodes_updated)


# Collection Status Broadcast Functions

async def broadcast_collection_started(
    collection_id: str,
    target: str,
    collector_type: str
) -> int:
    """
    Broadcast collection started event to all connected clients.
    
    Args:
        collection_id: Collection task ID
        target: Target being collected
        collector_type: Type of collector
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_collection_started(collection_id, target, collector_type)


async def broadcast_collection_progress(
    collection_id: str,
    entities_found: int,
    relationships_found: int,
    status: str,
    percentage: int
) -> int:
    """
    Broadcast collection progress to all connected clients.
    
    Args:
        collection_id: Collection task ID
        entities_found: Number of entities found
        relationships_found: Number of relationships found
        status: Collection status
        percentage: Progress percentage (0-100)
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_collection_progress(
        collection_id,
        {
            "entities_found": entities_found,
            "relationships_found": relationships_found,
            "status": status,
            "percentage": percentage
        }
    )


async def broadcast_collection_completed(
    collection_id: str,
    total_entities: int,
    total_relationships: int,
    duration: float
) -> int:
    """
    Broadcast collection completed event to all connected clients.
    
    Args:
        collection_id: Collection task ID
        total_entities: Total entities collected
        total_relationships: Total relationships collected
        duration: Duration in seconds
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_collection_completed(
        collection_id,
        total_entities,
        total_relationships,
        duration
    )


async def broadcast_collection_error(
    collection_id: str,
    error_message: str,
    error_type: str
) -> int:
    """
    Broadcast collection error to all connected clients.
    
    Args:
        collection_id: Collection task ID
        error_message: Error message
        error_type: Type of error
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_collection_error(
        collection_id,
        error_message,
        error_type
    )


# Analytics & Metrics Broadcast Functions

async def broadcast_graph_metrics(
    node_count: int,
    edge_count: int,
    graph_density: float,
    avg_degree: float
) -> int:
    """
    Broadcast graph metrics update to all connected clients.
    
    Args:
        node_count: Total number of nodes
        edge_count: Total number of edges
        graph_density: Graph density
        avg_degree: Average node degree
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_metrics(
        {
            "node_count": node_count,
            "edge_count": edge_count,
            "graph_density": graph_density,
            "avg_degree": avg_degree
        },
        metrics_type="graph"
    )


async def broadcast_risk_metrics(
    entity_id: str,
    new_risk_score: float,
    change_type: str
) -> int:
    """
    Broadcast risk score update to all connected clients.
    
    Args:
        entity_id: Entity ID
        new_risk_score: New risk score
        change_type: Type of change (increased, decreased, no_change)
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_metrics(
        {
            "entity_id": entity_id,
            "new_risk_score": new_risk_score,
            "change_type": change_type
        },
        metrics_type="risk"
    )


async def broadcast_anomaly_detected(
    anomaly_type: str,
    entities_involved: List[str],
    severity: str
) -> int:
    """
    Broadcast anomaly detection alert to all connected clients.
    
    Args:
        anomaly_type: Type of anomaly
        entities_involved: List of entity IDs involved
        severity: Severity level (low, medium, high, critical)
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_metrics(
        {
            "anomaly_type": anomaly_type,
            "entities_involved": entities_involved,
            "severity": severity
        },
        metrics_type="anomaly"
    )


# Notification Broadcast Functions

async def broadcast_notification_alert(
    message: str,
    alert_type: str = "info",
    severity: str = "info"
) -> int:
    """
    Broadcast notification alert to all connected clients.
    
    Args:
        message: Alert message
        alert_type: Type of alert
        severity: Severity level (info, warning, error, critical)
    
    Returns:
        int: Number of clients notified
    """
    ws_manager = get_websocket_manager()
    return await ws_manager.broadcast_alert(message, alert_type, severity)


# Throttled Broadcast Functions

async def broadcast_graph_metrics_throttled(
    node_count: int,
    edge_count: int,
    graph_density: float,
    avg_degree: float
) -> int:
    """
    Broadcast graph metrics with throttling (max 1Hz).
    
    Args:
        node_count: Total number of nodes
        edge_count: Total number of edges
        graph_density: Graph density
        avg_degree: Average node degree
    
    Returns:
        int: Number of clients notified (0 if throttled)
    """
    global last_metrics_broadcast
    
    now = datetime.now(timezone.utc)
    metrics_key = "graph"
    
    # Check if we should throttle
    if metrics_key in last_metrics_broadcast:
        time_since_last = (now - last_metrics_broadcast[metrics_key]).total_seconds()
        if time_since_last < METRICS_THROTTLE_SECONDS:
            return 0  # Throttled
    
    # Update timestamp and broadcast
    last_metrics_broadcast[metrics_key] = now
    return await broadcast_graph_metrics(node_count, edge_count, graph_density, avg_degree)


async def broadcast_risk_metrics_throttled(
    entity_id: str,
    new_risk_score: float,
    change_type: str
) -> int:
    """
    Broadcast risk metrics with throttling.
    
    Args:
        entity_id: Entity ID
        new_risk_score: New risk score
        change_type: Type of change
    
    Returns:
        int: Number of clients notified
    """
    # Risk updates are less frequent, so no throttling
    return await broadcast_risk_metrics(entity_id, new_risk_score, change_type)


# Background task to clean up old timestamps
async def cleanup_throttle_cache():
    """Clean up old timestamps from throttle cache"""
    global last_metrics_broadcast
    
    while True:
        try:
            await asyncio.sleep(60)  # Run every minute
            now = datetime.now(timezone.utc)
            
            # Remove entries older than 5 seconds
            to_remove = [
                key for key, timestamp in last_metrics_broadcast.items()
                if (now - timestamp).total_seconds() > 5
            ]
            
            for key in to_remove:
                del last_metrics_broadcast[key]
                
        except Exception as e:
            logger.error(f"Error cleaning throttle cache: {e}")


# Start cleanup task
asyncio.create_task(cleanup_throttle_cache())