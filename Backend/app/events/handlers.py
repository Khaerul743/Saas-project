from app.events.redis_event import EventType, event_bus
from app.utils.logger import get_logger
from typing import Dict, Any
import asyncio

logger = get_logger(__name__)

async def document_uploaded_handler(event_data: Dict[str, Any]):
    event_type = event_data.get("event_type")
    user_id = event_data.get("user_id")
    agent_id = event_data.get("agent_id")
    if event_type == EventType.DOCUMENT_UPLOADED:
        logger.info(f"Document uploaded: {event_data} by user {user_id} and agent {agent_id}")

event_bus.subscribe(EventType.DOCUMENT_UPLOADED, document_uploaded_handler)
