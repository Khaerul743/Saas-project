import json
from typing import Any, Dict

from redis.asyncio import Redis

from app.configs.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RedisStorage:
    def __init__(self):
        self.redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

    async def store_agent(self, agent_id: str, agent_obj: Any):
        try:
            key = f"agent:{agent_id}"
            await self.redis_client.set(key, json.dumps(agent_obj))
            logger.info(f"Agent {agent_id} stored in Redis")
            return True
        except Exception as e:
            logger.error(f"Error while storing agent {agent_id} in Redis: {str(e)}")
            raise

    async def get_agent(self, agent_id: str):
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

    async def is_agent_exists(self, agent_id: str):
        try:
            key = f"agent:{agent_id}"
            return await self.redis_client.exists(key)
        except Exception as e:
            logger.error(
                f"Error while checking if agent {agent_id} exists in Redis: {str(e)}"
            )
            raise

    async def update_simple_rag_agent(self, agent_id: str, data: Dict[str, Any]):
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                logger.warning(f"Agent not found : {agent_id}")
                return False

            # Update semua key yang dikirim lewat data
            for key, value in data.items():
                agent[key] = value

            # Simpan ulang ke Redis
            await self.store_agent(agent_id, agent)
            logger.info(f"Agent {agent_id} updated successfully: {data}")
            return True
        except Exception as e:
            logger.error(f"Error while updating agent from redis storage: {str(e)}")
            return False

    async def update_customer_service_agent(self, agent_id: str, data: Dict[str, Any]):
        try:
            company_keys = {
                "company_name",
                "industry",
                "company_description",
                "address",
                "email",
                "website",
                "fallback_email",
            }
            agent = await self.get_agent(agent_id)
            if not agent:
                logger.warning(f"Agent not found : {agent_id}")
                return False
            # print(f"Before update: {agent}")

            # Update semua key yang dikirim lewat data
            for key, value in data.items():
                if key in agent:
                    agent[key] = value
                elif key in company_keys:
                    if key == "company_name":
                        key = "name"
                    elif key == "company_description":
                        key = "description"
                    if "company_information" not in agent:
                        agent["company_information"] = {}
                    agent["company_information"][key] = value

            # Simpan ulang ke Redis
            # print(f"After update: {agent}")
            await self.store_agent(agent_id, agent)

            logger.info(f"Agent {agent_id} updated successfully: {data}")
            return True
        except Exception as e:
            logger.error(f"Error while updating agent from redis storage: {str(e)}")
            return False

    async def remove_agent(self, agent_id: str):
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

    async def get_agent_state_checkpoint(self, thread_id: str):
        try:
            pattern = f"checkpoint:{thread_id}:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                data = await self.redis_client.execute_command("JSON.GET", key)
                if data:
                    parsed = json.loads(data)
                    logger.info(f"Checkpoint found for {thread_id}: {key}")
                    return parsed.get("checkpoint", "")
            logger.warning(f"No checkpoint found for thread_id: {thread_id}")
            return None
        except Exception as e:
            logger.error(
                f"Error while getting checkpoint {thread_id} from Redis: {str(e)}"
            )
            raise

    async def get_all_state_checkpoints(self):
        """Menampilkan semua checkpoint LangGraph yang tersimpan di Redis."""
        try:
            checkpoints = []

            # Ambil semua key dengan prefix "checkpoint:"
            async for key in self.redis_client.scan_iter(match="checkpoint:*"):
                # Skip key turunan (write / blobs)
                if key.startswith("checkpoint_write:") or key.startswith(
                    "checkpoint_blobs:"
                ):
                    continue

                try:
                    data = await self.redis_client.execute_command("JSON.GET", key)
                    if not data:
                        continue

                    parsed = json.loads(data)
                    # Ekstrak info penting
                    parts = key.split(":")
                    checkpoint = {
                        "key": key,
                        "thread_id": parts[1] if len(parts) > 1 else None,
                        "namespace": parts[2] if len(parts) > 2 else None,
                        "checkpoint_id": parts[3] if len(parts) > 3 else None,
                        "values": parsed.get("values", {}),
                    }
                    checkpoints.append(checkpoint)

                except Exception as e:
                    logger.warning(f"Gagal parse checkpoint {key}: {e}")

            if not checkpoints:
                logger.info("Tidak ada checkpoint yang tersimpan di Redis.")
                return []

            logger.info(f"Ditemukan {len(checkpoints)} checkpoint di Redis.")
            return checkpoints

        except Exception as e:
            logger.error(f"Error saat mengambil daftar checkpoint: {str(e)}")
            raise

    async def delete_agent_checkpoints(self, thread_id: str):
        try:
            # Daftar prefix yang digunakan LangGraph
            prefixes = [
                f"checkpoint:{thread_id}:*",
                f"checkpoint_write:{thread_id}:*",
                f"checkpoint_blobs:{thread_id}:*",
            ]

            total_deleted = 0

            for pattern in prefixes:
                async for key in self.redis_client.scan_iter(match=pattern):
                    await self.redis_client.delete(key)
                    total_deleted += 1
                    logger.debug(f"Deleted key: {key}")

            if total_deleted > 0:
                logger.info(
                    f"Deleted {total_deleted} checkpoint keys for thread_id={thread_id}"
                )
            else:
                logger.warning(f"No checkpoint keys found for thread_id={thread_id}")

            return total_deleted

        except Exception as e:
            logger.error(f"Error deleting checkpoints for {thread_id}: {str(e)}")
            raise


redis_storage = RedisStorage()
