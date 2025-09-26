import asyncio
from typing import Any, Dict

from app.events.redis_event import Event, EventType, event_bus
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def document_uploaded_handler(event_data: Event):
    print(f"event_data: {event_data.event_type.value}")
    event_type = event_data.event_type
    user_id = event_data.user_id
    agent_id = event_data.agent_id
    if event_type == EventType.DOCUMENT_UPLOADED:
        logger.info(
            f"Document uploaded: {event_data} by user {user_id} and agent {agent_id}"
        )


# event_bus.subscribe(EventType.DOCUMENT_UPLOADED, document_uploaded_handler)
