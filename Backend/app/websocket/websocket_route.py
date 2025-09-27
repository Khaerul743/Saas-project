"""
WebSocket routes for real-time communication
"""
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.websocket.connection_manager import manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/agent-progress/{user_id}")
async def websocket_agent_progress(
    websocket: WebSocket,
    user_id: int,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for agent creation progress updates
    
    Args:
        websocket: WebSocket connection
        user_id: User ID for the connection
        token: Optional authentication token
    """
    try:
        # Add connection to manager
        await manager.connect(websocket, user_id)
        
        logger.info(f"WebSocket connected for agent progress - User: {user_id}")
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "Connected to agent progress updates",
            "user_id": user_id
        }, user_id)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, user_id)
                elif message.get("type") == "subscribe_task":
                    task_id = message.get("task_id")
                    if task_id:
                        manager.add_task_connection(websocket, task_id)
                        await manager.send_personal_message({
                            "type": "task_subscribed",
                            "task_id": task_id
                        }, user_id)
                elif message.get("type") == "unsubscribe_task":
                    task_id = message.get("task_id")
                    if task_id:
                        manager.remove_task_connection(websocket, task_id)
                        await manager.send_personal_message({
                            "type": "task_unsubscribed",
                            "task_id": task_id
                        }, user_id)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user_id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Internal server error"
                }, user_id)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)


@router.websocket("/task-status/{task_id}")
async def websocket_task_status(
    websocket: WebSocket,
    task_id: str,
    user_id: Optional[int] = Query(None)
):
    """
    WebSocket endpoint for specific task status updates
    
    Args:
        websocket: WebSocket connection
        task_id: Task ID to monitor
        user_id: Optional user ID for authentication
    """
    try:
        # Add connection to manager
        if user_id:
            await manager.connect(websocket, user_id)
        
        # Add to task-specific connections
        manager.add_task_connection(websocket, task_id)
        
        logger.info(f"WebSocket connected for task status - Task: {task_id}, User: {user_id}")
        
        # Send welcome message
        await manager.send_task_message({
            "type": "connection_established",
            "message": f"Connected to task {task_id} updates",
            "task_id": task_id
        }, task_id)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_task_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp"),
                        "task_id": task_id
                    }, task_id)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_task_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "task_id": task_id
                }, task_id)
            except Exception as e:
                logger.error(f"Error handling task WebSocket message: {e}")
                await manager.send_task_message({
                    "type": "error",
                    "message": "Internal server error",
                    "task_id": task_id
                }, task_id)
    
    except WebSocketDisconnect:
        logger.info(f"Task WebSocket disconnected - Task: {task_id}")
    except Exception as e:
        logger.error(f"Task WebSocket error - Task: {task_id}, Error: {e}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)
        manager.remove_task_connection(websocket, task_id)


@router.get("/connections")
async def get_connection_info():
    """Get WebSocket connection information"""
    return {
        "total_connections": manager.get_connection_count(),
        "user_connections": manager.get_user_connections(),
        "active_tasks": list(manager.task_connections.keys())
    }