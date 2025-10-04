import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List

from redis import asyncio as ioredis

from app.configs.config import settings
from app.utils.logger import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


class EventType(Enum):
    AGENT_CREATION_PROGRESS = "event.agent.progress"
    AGENT_CREATION_SUCCESS = "event.agent.success"
    AGENT_CREATION_FAILURE = "event.agent.failure"
    AGENT_INVOKE = "event.agent.invoke"


@dataclass
class Event:
    event_type: EventType
    user_id: int
    agent_id: str
    payload: Dict[str, Any]
    datetime = datetime.now()

    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "payload": self.payload,
            "timestamp": datetime.utcnow().isoformat(),
        }


class EventBus:
    def __init__(self):
        self.redis_client = ioredis.Redis(
            host=getattr(settings, "REDIS_HOST"),
            port=getattr(settings, "REDIS_PORT"),
            db=getattr(settings, "REDIS_DB"),
        )
        self.pubsub = self.redis_client.pubsub()
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._is_running = False

    async def publish(self, event: Event):
        try:
            event_data = event.to_dict()
            user_id = event_data.get("user_id")
            event_type = event_data.get("event_type")
            channel = f"{event_type}.user:{user_id}"

            await self.redis_client.publish(channel, json.dumps(event_data))
            logger.info(f"User with id {user_id} published to channel {channel}")

        except Exception as e:
            logger.error(f"Error while published event: {str(e)}")
            raise

    def subscribe(self, event_type: EventType, handler: Callable):
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
            logger.info(f"Subscribe event type {event_type.value}")
        except Exception as e:
            logger.error(f"Error while subscribe the event: {str(e)}")
            raise

    async def _handler_message(self, message: Dict[str, Any]):
        try:
            event_type = EventType(message["event_type"])
            logger.info(
                f"The handler function accepted the message: event type {event_type}"
            )
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    await handler(message)
            else:
                logger.warning(f"Event type not in subscribers: {event_type}")
                print(f"List subscribers: {self._subscribers}")
        except Exception as e:
            logger.error(f"Error while handler the message: {e}")
            raise e

    async def _listening_loop(self):
        try:
            while self._is_running:
                message = await self.pubsub.get_message()
                if message and message["type"] == "pmessage":
                    data = json.loads(message["data"])
                    logger.info("Sending the message to handler function")
                    await self._handler_message(data)
                elif message and message["type"] == "message":
                    print(f"Message accepted: {message}")

                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error while running the listening loop: {str(e)}")
            raise e

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        pattern = [f"{event_type.value}.user:*" for event_type in EventType]
        await self.pubsub.psubscribe(*pattern)
        logger.info(f"Subscribe to channel: {pattern}")
        asyncio.create_task(self._listening_loop())

    async def stop_listening(self):
        """Stop listening for events"""
        self._is_running = False
        await self.pubsub.punsubscribe()
        await self.pubsub.close()
        print("Stopped listening for Redis events")


event_bus = EventBus()
