from app.events.redis_event import EventType, event_bus
from app.utils.logger import get_logger
from typing import Dict, Any
import asyncio

logger = get_logger(__name__)

async def document_uploaded_handler(event_data: Dict[str, Any]):