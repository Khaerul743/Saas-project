from dataclasses import dataclass
from typing import Literal

from src.core.exceptions.integration_exceptions import IntegrationIsAlreadyExist
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IIntergrationRepository, IPlatformReporitory


@dataclass
class CreateIntegrationInput:
    agent_id: str
    platform: Literal["whatsapp", "telegram", "api"]
    status: Literal["active", "non-active"]
    api_key: str


@dataclass
class CreateIntegrationOutput:
    integration_id: int
    platform_id: int


class CreateIntegration(BaseUseCase[CreateIntegrationInput, CreateIntegrationOutput]):
    def __init__(
        self,
        integration_repository: IIntergrationRepository,
        platform_repository: IPlatformReporitory,
    ):
        self.integration_repository = integration_repository
        self.platform_repository = platform_repository

    async def execute(
        self, input_data: CreateIntegrationInput
    ) -> UseCaseResult[CreateIntegrationOutput]:
        try:
            # Check integration
            integration = await self.integration_repository.get_by_agent_and_platform(
                input_data.agent_id, input_data.platform
            )
            if integration:
                return UseCaseResult.error_result(
                    "Integration is already exist", IntegrationIsAlreadyExist()
                )

            # Add new integration to database
            add_new_integration = await self.integration_repository.add_new_integration(
                input_data.agent_id, input_data.platform, input_data.status
            )

            # Add new integration platform to database
            add_new_platform = await self.platform_repository.add_new_platform(
                add_new_integration.id, input_data.platform, input_data.api_key
            )

            return UseCaseResult.success_result(
                CreateIntegrationOutput(add_new_integration.id, add_new_platform.id)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while creating integration: {str(e)}", e
            )
