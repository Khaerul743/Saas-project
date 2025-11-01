import asyncio
import os

import aiohttp
from dotenv import load_dotenv

from src.core.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


async def set_webhook(api_key: str, integration_id):
    url = f"https://api.telegram.org/bot{api_key}/setWebhook"
    webhook_url = (
        f"{os.environ.get('THIS_APP_URL')}/api/telegram/webhook/{integration_id}"
    )
    print(f"Webhook url: {webhook_url}")
    payload = {"url": webhook_url}
    print(webhook_url)
    try:
        timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False), timeout=timeout
        ) as session:
            async with session.post(url, json=payload) as response:
                resp_json = await response.json()
                if response.status == 200 and resp_json.get("ok"):
                    logger.info(f"Set webhook is successfully: {resp_json}")
                    return {"status": True, "response": resp_json}
                else:
                    logger.warning(f"Failed to set webhook: {resp_json}")
                    return {"status": False, "response": resp_json}
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }


async def send_message(api_key: str, chat_id, message: str):
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
                    logger.info(f"Message sent successfully: {resp_json}")
                    return {"status": True, "response": resp_json}
                else:
                    logger.warning(f"Failed to send message: {resp_json}")
                    return {"status": False, "response": resp_json}
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }


async def delete_webhook(api_key: str):
    url = f"https://api.telegram.org/bot{api_key}/deleteWebhook"
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url) as response:
                resp_json = await response.json()
                if response.status == 200 and resp_json.get("ok"):
                    logger.info(f"Delete webhook is successfully: {resp_json}")
                    return {"status": True, "response": resp_json}
                else:
                    logger.warning(f"Failed to delete webhook: {resp_json}")
                    return {"status": False, "response": resp_json}
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "status": False,
            "response": "Internal server error, please try again later.",
        }


# Example usage:
# asyncio.run(set_webhook("your_api_key", "your_integration_id"))
