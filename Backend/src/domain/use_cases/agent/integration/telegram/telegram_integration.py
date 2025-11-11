from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.telegram import TelegramManager

from ..api.api_integration import IntegrationOutput
from ..create_integration import CreateIntegration, CreateIntegrationInput

load_dotenv()


@dataclass
class TelegramIntegrationInput:
    agent_id: str
    api_key: str
    status: Literal["active", "non-active"]


class TelegramIntegration(BaseUseCase[TelegramIntegrationInput, IntegrationOutput]):
    def __init__(
        self,
        create_integration_usecase: CreateIntegration,
        telegram_manager: TelegramManager,
    ):
        self.create_integration = create_integration_usecase
        self.telegram_manager = telegram_manager

    async def execute(
        self, input_data: TelegramIntegrationInput
    ) -> UseCaseResult[IntegrationOutput]:
        try:
            # Add new integration to database
            create_new_integration = await self.create_integration.execute(
                CreateIntegrationInput(
                    input_data.agent_id,
                    "telegram",
                    input_data.status,
                    input_data.api_key,
                )
            )
            if not create_new_integration.is_success():
                return self._return_exception(create_new_integration)

            integration_data = create_new_integration.get_data()
            if not integration_data:
                return UseCaseResult.error_result(
                    "Create integration use case is not returned the data",
                    RuntimeError(
                        "Create integration use case is not returned the data"
                    ),
                )

            # Set telegram webhook
            await self.telegram_manager.set_webhook(
                input_data.api_key, input_data.agent_id
            )

            return UseCaseResult.success_result(
                IntegrationOutput(
                    integration_data.integration_id,
                    integration_data.platform_id,
                    input_data.api_key,
                )
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while creating telegram integration: {str(e)}", e
            )
