from typing import Any, Dict

from app.events.redis_event import EventType, event_bus
from app.utils.logger import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


async def send_agent_progress(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        await ws_manager.send_to_user(user_id, message)
    except Exception as e:
        logger.error(f"Error while send agent progress: {e}")
        raise e


async def send_agent_success(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        await ws_manager.send_to_user(user_id, message)
    except Exception as e:
        logger.error(f"Error while send agent success: {e}")
        raise e


event_bus.subscribe(EventType.AGENT_CREATION_PROGRESS, send_agent_progress)
event_bus.subscribe(EventType.AGENT_CREATION_SUCCESS, send_agent_success)
