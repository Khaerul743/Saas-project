from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.telegram_schema import TelegramSendMessage
from src.core.exceptions.integration_exceptions import TelegramResponseException
from src.domain.service.webhook_service import WebhookService


class WebhookController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.webhook_service = WebhookService(db, request)

    async def invoke_telegram_agent(self, data: dict[str, Any]):
        try:
            payload = TelegramSendMessage(
                agent_id=data["agent_id"],
                username=data["username"],
                chat_id=data["chat_id"],
                text=data["text"],
            )
            print(f"PayloadddddddddMMEk:{payload}")
            await self.webhook_service.invoked_agent_and_send_to_telegram(payload)

        except TelegramResponseException as e:
            raise e

        except Exception as e:
            raise TelegramResponseException()
