import asyncio
from typing import Any, Dict

from app.events.redis_event import Event, EventType, event_bus
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def agent_creation_progress_handler(event_data: Event):
    print(f"event_data: {event_data.event_type.value}")
    event_type = event_data.event_type
    user_id = event_data.user_id
    agent_id = event_data.agent_id
    if event_type == EventType.AGENT_CREATION_PROGRESS:
        logger.info(
            f"agent progress: {event_data.data} by user {user_id} and agent {agent_id}"
        )


event_bus.subscribe(EventType.AGENT_CREATION_PROGRESS, agent_creation_progress_handler)
