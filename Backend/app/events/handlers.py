"""
Event handlers for Redis events with WebSocket integration
"""
from typing import Any, Dict

from app.events.redis_event import Event, EventType, event_bus
from app.websocket.websocket_handler import websocket_handler
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def agent_creation_progress_handler(event_data: Event):
    """Handle agent creation progress events"""
    print(f"event_data: {event_data.event_type.value}")
    event_type = event_data.event_type
    user_id = event_data.user_id
    agent_id = event_data.agent_id
    
    if event_type == EventType.AGENT_CREATION_PROGRESS:
        logger.info(
            f"agent progress: {event_data.data} by user {user_id} and agent {agent_id}"
        )
        
        # Forward to WebSocket
        await websocket_handler.handle_agent_creation_progress(event_data)


async def agent_creation_success_handler(event_data: Event):
    """Handle agent creation success events"""
    print(f"event_data: {event_data.event_type.value}")
    event_type = event_data.event_type
    user_id = event_data.user_id
    agent_id = event_data.agent_id
    
    if event_type == EventType.AGENT_CREATION_SUCCESS:
        logger.info(
            f"agent creation success: {event_data.data} by user {user_id} and agent {agent_id}"
        )
        
        # Forward to WebSocket
        await websocket_handler.handle_agent_creation_success(event_data)


async def agent_creation_failed_handler(event_data: Event):
    """Handle agent creation failure events"""
    print(f"event_data: {event_data.event_type.value}")
    event_type = event_data.event_type
    user_id = event_data.user_id
    agent_id = event_data.agent_id
    
    if event_type == EventType.AGENT_CREATION_FAILED:
        logger.error(
            f"agent creation failed: {event_data.data} by user {user_id} and agent {agent_id}"
        )
        
        # Forward to WebSocket
        await websocket_handler.handle_agent_creation_failed(event_data)


# Register all handlers
event_bus.subscribe(EventType.AGENT_CREATION_PROGRESS, agent_creation_progress_handler)
event_bus.subscribe(EventType.AGENT_CREATION_SUCCESS, agent_creation_success_handler)
event_bus.subscribe(EventType.AGENT_CREATION_FAILED, agent_creation_failed_handler)