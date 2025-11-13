import os
from typing import Any, Dict

import aiohttp

from src.core.utils.logger import get_logger


class TelegramManager:
    def __init__(self):
        self._list_telegram_user: Dict[str, Dict[str, Any]] = {}
        self._logger = get_logger(__name__)

    async def set_webhook(self, api_key: str, agent_id: str) -> dict[str, Any]:
        url = f"https://api.telegram.org/bot{api_key}/setWebhook"
        webhook_url = (
            f"{os.environ.get('THIS_APP_URL')}/api/webhook/telegram/{agent_id}"
        )
        print(f"Webhook url: {webhook_url}")
        payload = {"url": webhook_url}
        try:
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False), timeout=timeout
            ) as session:
                async with session.post(url, json=payload) as response:
                    resp_json = await response.json()
                    if response.status == 200 and resp_json.get("ok"):
                        # Ensure there is an entry for this agent before assigning
                        if agent_id not in self._list_telegram_user:
                            self._list_telegram_user[agent_id] = {}
                        self._list_telegram_user[agent_id]["api_key"] = api_key
                        return {"status": True, "response": resp_json}
                    else:
                        raise RuntimeError(
                            "Failed to set webhook: Telegram response is not ok"
                        )
        except aiohttp.ClientError as e:
            raise e
        except Exception as e:
            raise e

    async def send_message(self, agent_id: str, api_key: str, chat_id, message: str):
        url = f"https://api.telegram.org/bot{api_key}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}

        try:
            timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout for messages
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False), timeout=timeout
            ) as session:
                async with session.post(url, json=payload) as response:
                    resp_json = await response.json()
                    if response.status == 200 and resp_json.get("ok"):
                        # Ensure agent entry exists and set chat_id only when appropriate
                        agent = self._list_telegram_user.get(agent_id)
                        if agent is None:
                            # If there is no entry for this agent, create one with api_key and chat_id
                            self._list_telegram_user[agent_id] = {
                                "api_key": api_key,
                                "chat_id": chat_id,
                            }
                        else:
                            # If chat_id not set yet and api_key matches, store chat_id
                            if agent.get("chat_id", None) is None:
                                if agent.get("api_key") == api_key:
                                    agent["chat_id"] = chat_id

                        return {"status": True, "response": resp_json}
                    else:
                        return {"status": False, "response": resp_json}
        except aiohttp.ClientError as e:
            self._logger.error(str(e))
            return {
                "status": False,
                "response": "Internal server error, please try again later.",
            }

        except Exception as e:
            self._logger.error(
                f"Unexpected error while sendng telegram message: {str(e)}"
            )
            return {
                "status": False,
                "response": "Internal server error, please try again later.",
            }

    async def delete_webhook(self, api_key: str):
        url = f"https://api.telegram.org/bot{api_key}/deleteWebhook"
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.get(url) as response:
                    resp_json = await response.json()
                    if response.status == 200 and resp_json.get("ok"):
                        self._logger.info(
                            f"Delete webhook is successfully: {resp_json}"
                        )
                        return {"status": True, "response": resp_json}
                    else:
                        self._logger.warning(f"Failed to delete webhook: {resp_json}")
                        return {"status": False, "response": resp_json}
        except aiohttp.ClientError as e:
            self._logger.error(f"HTTP error occurred: {e}")
            return {
                "status": False,
                "response": "Internal server error, please try again later.",
            }
        except Exception as e:
            self._logger.error(f"Unexpected error: {e}")
            return {
                "status": False,
                "response": "Internal server error, please try again later.",
            }


telegram_manager = TelegramManager()
