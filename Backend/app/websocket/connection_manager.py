"""
WebSocket connection manager for real-time communication
"""
import json
from typing import Dict, List, Set
from fastapi import WebSocket
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store connections by task_id for task-specific updates
        self.task_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection and add to user's connections"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remove empty user connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    def add_task_connection(self, websocket: WebSocket, task_id: str):
        """Add WebSocket connection for specific task"""
        if task_id not in self.task_connections:
            self.task_connections[task_id] = set()
        
        self.task_connections[task_id].add(websocket)
        logger.info(f"WebSocket added for task {task_id}")
    
    def remove_task_connection(self, websocket: WebSocket, task_id: str):
        """Remove WebSocket connection for specific task"""
        if task_id in self.task_connections:
            self.task_connections[task_id].discard(websocket)
            
            # Remove empty task connections
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
    
    async def send_task_message(self, message: dict, task_id: str):
        """Send message to specific task connections"""
        if task_id in self.task_connections:
            disconnected = set()
            
            for connection in self.task_connections[task_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to task {task_id}: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.task_connections[task_id].discard(connection)
    
    async def broadcast_to_user(self, message: dict, user_id: int):
        """Broadcast message to all connections of a user"""
        await self.send_personal_message(message, user_id)
    
    def get_connection_count(self, user_id: int = None) -> int:
        """Get number of active connections"""
        if user_id:
            return len(self.active_connections.get(user_id, set()))
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_user_connections(self) -> Dict[int, int]:
        """Get connection count per user"""
        return {user_id: len(connections) for user_id, connections in self.active_connections.items()}


# Global connection manager instance
manager = ConnectionManager()