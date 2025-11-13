from dataclasses import dataclass
from typing import Literal

from src.core.exceptions.integration_exceptions import (
    IntegrationNotFoundException,
    TelegramApiKeyNotFound,
)
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IApiKeyRepository, IIntergrationRepository
from src.infrastructure.telegram import TelegramManager


@dataclass
class DeleteTelegramIntegrationInput:
    agent_id: str
    platform: Literal["telegram"]


@dataclass
class DeleteTelegramIntegrationOutput:
    success: bool


class DeleteTelegramIntegration(
    BaseUseCase[DeleteTelegramIntegrationInput, DeleteTelegramIntegrationOutput]
):
    def __init__(
        self,
        api_key_repository: IApiKeyRepository,
        integration_repository: IIntergrationRepository,
        telegram_manager: TelegramManager,
    ):
        self.api_key_repository = api_key_repository
        self.integration_repository = integration_repository
        self.telegram_manager = telegram_manager

    async def execute(
        self, input_data: DeleteTelegramIntegrationInput
    ) -> UseCaseResult[DeleteTelegramIntegrationOutput]:
        try:
            # Check integration exists
            integration = await self.integration_repository.get_by_agent_and_platform(
                input_data.agent_id, input_data.platform
            )

            if not integration:
                return UseCaseResult.error_result(
                    "Integration not found", IntegrationNotFoundException()
                )

            # Delete webhook from Telegram
            telegram_api_key = (
                await self.api_key_repository.get_telegram_api_key_by_agent_id(
                    input_data.agent_id
                )
            )

            if not telegram_api_key:
                return UseCaseResult.error_result(
                    "Telegram api key not found",
                    TelegramApiKeyNotFound(
                        "Make sure the agent is integration with telegram platform"
                    ),
                )

            delete_resp = await self.telegram_manager.delete_webhook(telegram_api_key)
            if not delete_resp.get("status"):
                return UseCaseResult.error_result(
                    "Failed to delete telegram webhook",
                    RuntimeError("Failed to delete telegram webhook"),
                )

            # Delete integration (cascade removes platform config)
            await self.integration_repository.delete_by_id(integration.id)  # type: ignore[attr-defined]

            return UseCaseResult.success_result(
                DeleteTelegramIntegrationOutput(success=True)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while deleting telegram integration: {str(e)}", e
            )
