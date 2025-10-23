# """
# Event publishing utilities for Celery tasks
# """
# import asyncio
# from datetime import datetime
# from typing import Optional

from app.events.redis_event import Event, EventType, event_bus
from app.core.logger import get_logger
from app.events.loop_manager import run_async
from typing import Optional

logger = get_logger(__name__)


def publish_agent_event(
    event_type: EventType,
    user_id: int,
    agent_id: int,
    payload: dict,
):
    """Publish agent event"""
    logger.info(
        f"Published {event_type.value} event for agent {agent_id} for user {user_id}"
    )
    run_async(
        event_bus.publish(
            Event(
                event_type=event_type,
                user_id=user_id,
                agent_id=agent_id,
                payload=payload,
            )
        )
    )


# def _get_or_create_event_loop():
#     """Get existing event loop or create new one safely"""
#     try:
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             # If loop is running, create new one
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#         return loop
#     except RuntimeError:
#         # No event loop exists, create new one
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         return loop


# def _ensure_event_bus_running():
#     """Ensure event bus is running in Celery worker"""
#     if not event_bus._is_running:
#         logger.info("Starting event bus in Celery worker")
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             loop.run_until_complete(event_bus.start())
#             logger.info("Event bus started in Celery worker")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to start event bus: {e}")
#             return False
#     return True


# def publish_agent_event(
#     event_type: EventType,
#     user_id: int,
#     agent_id: int,
#     data: dict,
#     status: str = "processing",
#     task_id: Optional[str] = None
# ) -> bool:
#     """
#     Publish agent-related event to Redis event bus

#     Args:
#         event_type: Type of event to publish
#         user_id: ID of the user
#         agent_id: ID of the agent
#         data: Event data payload
#         status: Status of the operation
#         task_id: Optional task ID for WebSocket routing

#     Returns:
#         bool: True if event was published successfully, False otherwise
#     """
#     try:
#         # Ensure event bus is running
#         if not _ensure_event_bus_running():
#             return False

#         # Get or create event loop
#         loop = _get_or_create_event_loop()

#         # Add task_id to data if provided
#         event_data = {**data, "status": status}
#         if task_id:
#             event_data["task_id"] = task_id

#         # Create and publish event
#         event = Event(
#             event_type=event_type,
#             timestamp=datetime.now(),
#             data=event_data,
#             user_id=user_id,
#             agent_id=agent_id,
#         )

#         loop.run_until_complete(event_bus.publish(event))
#         logger.info(f"Published {event_type.value} event for agent {agent_id}")
#         return True

#     except Exception as e:
#         logger.error(f"Failed to publish {event_type.value} event: {e}")
#         return False


# def publish_agent_progress_event(
#     user_id: int,
#     agent_id: int,
#     current: int,
#     total: int,
#     status: str,
#     task_id: Optional[str] = None
# ) -> bool:
#     """Publish agent creation progress event"""
#     return publish_agent_event(
#         event_type=EventType.AGENT_CREATION_PROGRESS,
#         user_id=user_id,
#         agent_id=agent_id,
#         data={"current": current, "total": total},
#         status=status,
#         task_id=task_id
#     )


# def publish_agent_success_event(
#     user_id: int,
#     agent_id: int,
#     additional_data: Optional[dict] = None,
#     task_id: Optional[str] = None
# ) -> bool:
#     """Publish agent creation success event"""
#     data = {"agent_id": agent_id}
#     if additional_data:
#         data.update(additional_data)

#     return publish_agent_event(
#         event_type=EventType.AGENT_CREATION_SUCCESS,
#         user_id=user_id,
#         agent_id=agent_id,
#         data=data,
#         status="completed",
#         task_id=task_id
#     )


# def publish_agent_failure_event(
#     user_id: int,
#     agent_id: int,
#     error_message: str,
#     additional_data: Optional[dict] = None,
#     task_id: Optional[str] = None
# ) -> bool:
#     """Publish agent creation failure event"""
#     data = {"error": error_message}
#     if additional_data:
#         data.update(additional_data)

#     return publish_agent_event(
#         event_type=EventType.AGENT_CREATION_FAILED,
#         user_id=user_id,
#         agent_id=agent_id,
#         data=data,
#         status="failed",
#         task_id=task_id
#     )
