import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List

import redis.asyncio as redis

from app.configs.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    AGENT_CREATION_PROGRESS = "agent.creation.progress"
    AGENT_CREATION_SUCCESS = "agent.creation.success"
    AGENT_CREATION_FAILED = "agent.creation.failed"


@dataclass
class Event:
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    user_id: int
    agent_id: int


class RedisEventBus:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST"),
            port=getattr(settings, "REDIS_PORT"),
            db=getattr(settings, "REDIS_DB"),
            decode_responses=True,
        )
        self.pubsub = self.redis_client.pubsub()
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._is_running = False

    async def publish(self, event: Event):
        try:
            event_data = {
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "user_id": event.user_id,
                "agent_id": event.agent_id,
            }
            channel = f"ai.events.user:{event.user_id}.{event.event_type.value}"
            await self.redis_client.publish(channel, json.dumps(event_data))
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise e

    def subscribe(self, event_type: EventType, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    async def _handle_message(self, message: Any):
        try:
            event_data = json.loads(message)
            event_type = EventType(event_data["event_type"])
            event = Event(
                event_type=event_type,
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                data=event_data["data"],
                user_id=event_data["user_id"],
                agent_id=event_data["agent_id"],
            )
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    await callback(event)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            raise e

    async def _listening_loop(self):
        try:
            while self._is_running:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    # Handle both regular messages and pattern messages
                    if message.get("type") == "pmessage":
                        # Pattern message - extract channel from pattern
                        channel = message.get("channel")
                        data = message.get("data")
                        logger.debug(f"Pattern message received on channel: {channel}")
                        await self._handle_message(data)
                    elif message.get("type") == "message":
                        # Regular message
                        data = message.get("data")
                        logger.debug(f"Message received: {data}")
                        await self._handle_message(data)
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error listening to messages: {e}")
            raise e

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        
        # Use wildcard pattern subscription for production scalability
        # This allows receiving events for any user without hardcoding user IDs
        patterns = [f"ai.events.user:*" for event in EventType]
        await self.pubsub.psubscribe(*patterns)
        
        asyncio.create_task(self._listening_loop())
        logger.info(f"Redis event bus started with pattern subscription for {len(patterns)} patterns")

    async def stop_listening(self):
        """Stop listening for events"""
        self._is_running = False
        self.pubsub.unsubscribe()
        logger.info("Stopped listening for Redis events")


event_bus = RedisEventBus()
