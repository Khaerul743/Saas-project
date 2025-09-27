"""
WebSocket event handler for Redis events
"""
import json
from datetime import datetime
from typing import Dict, Any

from app.events.redis_event import Event, EventType
from app.websocket.connection_manager import manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketEventHandler:
    """Handles Redis events and forwards them to WebSocket connections"""
    
    def __init__(self):
        self.connection_manager = manager
    
    async def handle_agent_creation_progress(self, event: Event):
        """Handle agent creation progress events"""
        try:
            message = {
                "type": "agent_creation_progress",
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "user_id": event.user_id,
                "agent_id": event.agent_id,
                "message": f"Agent creation progress: {event.data.get('status', 'Processing')}"
            }
            
            # Send to user connections
            await self.connection_manager.broadcast_to_user(message, event.user_id)
            
            # Send to task-specific connections if task_id is available
            if "task_id" in event.data:
                await self.connection_manager.send_task_message(message, event.data["task_id"])
            
            logger.info(f"WebSocket: Sent agent progress to user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error handling agent creation progress: {e}")
    
    async def handle_agent_creation_success(self, event: Event):
        """Handle agent creation success events"""
        try:
            message = {
                "type": "agent_creation_success",
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "user_id": event.user_id,
                "agent_id": event.agent_id,
                "message": f"Agent created successfully! Agent ID: {event.agent_id}"
            }
            
            # Send to user connections
            await self.connection_manager.broadcast_to_user(message, event.user_id)
            
            # Send to task-specific connections if task_id is available
            if "task_id" in event.data:
                await self.connection_manager.send_task_message(message, event.data["task_id"])
            
            logger.info(f"WebSocket: Sent agent success to user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error handling agent creation success: {e}")
    
    async def handle_agent_creation_failed(self, event: Event):
        """Handle agent creation failure events"""
        try:
            message = {
                "type": "agent_creation_failed",
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "user_id": event.user_id,
                "agent_id": event.agent_id,
                "message": f"Agent creation failed: {event.data.get('error', 'Unknown error')}"
            }
            
            # Send to user connections
            await self.connection_manager.broadcast_to_user(message, event.user_id)
            
            # Send to task-specific connections if task_id is available
            if "task_id" in event.data:
                await self.connection_manager.send_task_message(message, event.data["task_id"])
            
            logger.info(f"WebSocket: Sent agent failure to user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error handling agent creation failure: {e}")
    
    async def handle_generic_event(self, event: Event):
        """Handle generic events"""
        try:
            message = {
                "type": "generic_event",
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "user_id": event.user_id,
                "agent_id": event.agent_id,
                "message": f"Event: {event.event_type.value}"
            }
            
            # Send to user connections
            await self.connection_manager.broadcast_to_user(message, event.user_id)
            
            logger.info(f"WebSocket: Sent generic event to user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error handling generic event: {e}")
    
    async def handle_event(self, event: Event):
        """Main event handler that routes events to specific handlers"""
        try:
            if event.event_type == EventType.AGENT_CREATION_PROGRESS:
                await self.handle_agent_creation_progress(event)
            elif event.event_type == EventType.AGENT_CREATION_SUCCESS:
                await self.handle_agent_creation_success(event)
            elif event.event_type == EventType.AGENT_CREATION_FAILED:
                await self.handle_agent_creation_failed(event)
            else:
                await self.handle_generic_event(event)
                
        except Exception as e:
            logger.error(f"Error in main event handler: {e}")
    
    async def send_custom_message(self, user_id: int, message: Dict[str, Any]):
        """Send custom message to user"""
        try:
            await self.connection_manager.broadcast_to_user(message, user_id)
            logger.info(f"WebSocket: Sent custom message to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending custom message: {e}")
    
    async def send_task_update(self, task_id: str, message: Dict[str, Any]):
        """Send task update to task-specific connections"""
        try:
            await self.connection_manager.send_task_message(message, task_id)
            logger.info(f"WebSocket: Sent task update for task {task_id}")
        except Exception as e:
            logger.error(f"Error sending task update: {e}")


# Global WebSocket event handler instance
websocket_handler = WebSocketEventHandler()


