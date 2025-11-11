from dataclasses import dataclass
from typing import Any, Literal

import aiohttp

from src.core.exceptions.integration_exceptions import TelegramApiKeyNotFound
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IApiKeyRepository
from src.infrastructure.telegram import TelegramManager


@dataclass
class SendTelegramUserMessageInput:
    agent_id: str
    chat_id: str | int
    message: str


@dataclass
class SendTelegramUserMessageOutput:
    success: bool


class SendTelegramUserMessage(
    BaseUseCase[SendTelegramUserMessageInput, SendTelegramUserMessageOutput]
):
    def __init__(
        self, api_key_repository: IApiKeyRepository, telegram_manager: TelegramManager
    ):
        self.api_key_repository = api_key_repository
        self.telegram_manager = telegram_manager

    async def execute(
        self, input_data: SendTelegramUserMessageInput
    ) -> UseCaseResult[SendTelegramUserMessageOutput]:
        try:
            telegram_api_key = (
                await self.api_key_repository.get_telegram_api_key_by_agent_id(
                    input_data.agent_id
                )
            )
            if not telegram_api_key:
                return UseCaseResult.error_result(
                    "Telegram api key not found", TelegramApiKeyNotFound()
                )
            send_message = await self.telegram_manager.send_message(
                input_data.agent_id,
                telegram_api_key,
                input_data.chat_id,
                input_data.message,
            )
            print(f"TELEGRAM STATUS: {send_message['status']}")
            if not send_message["status"]:
                return UseCaseResult.error_result(
                    "Failed to send telegram message",
                    RuntimeError("Failed to send telegram message"),
                )

            return UseCaseResult.success_result(
                SendTelegramUserMessageOutput(send_message["status"])
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while sending telegram message: {str(e)}", e
            )
