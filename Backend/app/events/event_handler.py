from typing import Any, Dict

from app.events.redis_event import EventType, event_bus
from app.dependencies.logger import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


async def send_agent_progress(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        payload = message.get("payload", {})
        await ws_manager.send_to_user(user_id, payload)
    except Exception as e:
        logger.error(f"Error while send agent progress: {e}")
        raise e


async def send_agent_success(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        payload = message.get("payload", {})
        payload["agent_id"] = message.get("agent_id")
        await ws_manager.send_to_user(user_id, payload)
    except Exception as e:
        logger.error(f"Error while send agent success: {e}")
        raise e


async def send_agent_failure(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        payload = message.get("payload", {})
        await ws_manager.send_to_user(user_id, payload)
    except Exception as e:
        logger.error(f"Error while send agent failure: {e}")
        raise e


async def send_agent_invoke(message: Dict[str, Any]):
    try:
        user_id = str(message.get("user_id"))
        await ws_manager.send_to_user(user_id, message)
    except Exception as e:
        logger.error(f"Error while send agent invoke: {e}")
        raise e


event_bus.subscribe(EventType.AGENT_CREATION_PROGRESS, send_agent_progress)
event_bus.subscribe(EventType.AGENT_CREATION_SUCCESS, send_agent_success)
event_bus.subscribe(EventType.AGENT_CREATION_FAILURE, send_agent_failure)
event_bus.subscribe(EventType.AGENT_INVOKE, send_agent_invoke)
