import json
from typing import Any
from redis.asyncio import Redis
from app.configs.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RedisStorage:
    def __init__(self):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=False,
        )
    
    async def store_agent(self, agent_id:str, agent_obj:Any):
        try:
            key = f"agent:{agent_id}"
            await self.redis_client.set(key, json.dumps(agent_obj))
            logger.info(f"Agent {agent_id} stored in Redis")
            return True
        except Exception as e:
            logger.error(f"Error while storing agent {agent_id} in Redis: {str(e)}")
            raise
    
    async def get_agent(self, agent_id:str):
        try:
            key = f"agent:{agent_id}"
            data = await self.redis_client.get(key)
            if data:
                logger.info(f"Agent {agent_id} retrieved from Redis")
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error while getting agent {agent_id} from Redis: {str(e)}")
            raise
    
    async def is_agent_exists(self, agent_id:str):
        try:
            key = f"agent:{agent_id}"
            return await self.redis_client.exists(key)
        except Exception as e:
            logger.error(f"Error while checking if agent {agent_id} exists in Redis: {str(e)}")
            raise
    

    async def remove_agent(self, agent_id:str):
        try:
            key = f"agent:{agent_id}"
            await self.redis_client.delete(key)
            logger.info(f"Agent {agent_id} removed from Redis")
            return True
        except Exception as e:
            logger.error(f"Error while removing agent {agent_id} from Redis: {str(e)}")
            raise
    
    async def get_all_agents(self):
        try:
            return await self.redis_client.keys("agent:*")
        except Exception as e:
            logger.error(f"Error while getting all agents from Redis: {str(e)}")
            raise
    
redis_storage = RedisStorage()