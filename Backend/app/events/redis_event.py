import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List

from configs.config import settings
from redis import asyncio as ioredis

from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    AGENT_CREATION_PROGRESS = "event.agent.progress"


@dataclass
class Event:
    event_type: EventType
    user_id: int
    agent_id: int
    payload: Dict[str, Any]
    datetime: datetime

    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "payload": self.payload,
            "datetime": self.datetime,
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
            channel = f"user:{user_id}{event_type}"

            await self.redis_client.publish(channel, json.dumps(event_data))
            logger.info(f"User with id {user_id} published event {event_type}")

        except Exception as e:
            logger.error(f"Error while published event: {str(e)}")
            raise

    def subscribe(self, event_type: EventType, handler: Callable):
        try:
            if event_type in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
            logger.info(f"Subscribe event type {event_type.value}")
        except Exception as e:
            logger.error(f"Error while subscribe the event: {str(e)}")
            raise

    async def _listening_loop(self):
        try:
            while self._is_running:
                message = await self.pubsub.get_message()
                if message and message["type"] == "message":
                    print(f"Message accepted: {message}")
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error while running the listening loop: {str(e)}")

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        channel = [event.value for event in EventType]
        await self.pubsub.subscribe(*channel)
        asyncio.create_task(self._listening_loop())

    async def stop_listening(self):
        """Stop listening for events"""
        self._is_running = False
        self.pubsub.unsubscribe()
        print("Stopped listening for Redis events")


event_bus = EventBus()
