import redis.asyncio as redis
import json 
import asyncio
from typing import Dict, Any, Callable, List
from enum import Enum
from app.configs.config import settings
from app.utils.logger import get_logger
from dataclasses import dataclass
from datetime import datetime

logger = get_logger(__name__)

class EventType(Enum):
    DOCUMENT_UPLOADED = "document.uploaded"

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
            channel = f"ai.events.{event.event_type.value}"
            await self.redis_client.publish(channel, json.dumps(event_data))
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise e
    
    def subscribe(self, event_type: EventType, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    async def _handler_message(self, message: Any):
        try:
            event_data = json.loads(message["data"])
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
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self._handler_message(message)
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error listening to messages: {e}")
            raise e
        
    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        channel = [f"ai.events.{event.value}" for event in EventType]
        await self.pubsub.subscribe(*channel)
        asyncio.create_task(self._listening_loop())
        logger.info("Redis event bus started")

    async def stop_listening(self):
        """Stop listening for events"""
        self._is_running = False
        self.pubsub.unsubscribe()
        logger.info("Stopped listening for Redis events")
    

event_bus = RedisEventBus()
    