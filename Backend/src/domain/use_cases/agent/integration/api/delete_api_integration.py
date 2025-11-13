from dataclasses import dataclass
from typing import Literal

from src.core.exceptions.integration_exceptions import IntegrationNotFoundException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IApiKeyRepository, IIntergrationRepository


@dataclass
class DeleteApiIntegrationInput:
    agent_id: str
    platform: Literal["api"]


@dataclass
class DeleteApiIntegrationOutput:
    success: bool


class DeleteApiIntegration(
    BaseUseCase[DeleteApiIntegrationInput, DeleteApiIntegrationOutput]
):
    def __init__(
        self,
        integration_repository: IIntergrationRepository,
        api_key_repository: IApiKeyRepository,
    ):
        self.integration_repository = integration_repository
        self.api_key_repository = api_key_repository

    async def execute(
        self, input_data: DeleteApiIntegrationInput
    ) -> UseCaseResult[DeleteApiIntegrationOutput]:
        try:
            integration = await self.integration_repository.get_by_agent_and_platform(
                input_data.agent_id, input_data.platform
            )

            if not integration:
                return UseCaseResult.error_result(
                    "Integration not found", IntegrationNotFoundException()
                )

            await self.integration_repository.delete_by_id(integration.id)  # type: ignore[attr-defined]
            await self.api_key_repository.delete_api_key_by_agent_id(
                input_data.agent_id
            )
            return UseCaseResult.success_result(
                DeleteApiIntegrationOutput(success=True)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while deleting API integration: {str(e)}", e
            )
