from dataclasses import dataclass
from typing import Literal

from src.core.exceptions.integration_exceptions import IntegrationIsAlreadyExist
from src.domain.use_cases.base import BaseUseCase, UseCaseResult

from ..create_integration import CreateIntegration, CreateIntegrationInput
from .generate_api_key import GenerateApiKey, GenerateApiKeyInput


@dataclass
class ApiIntegrationInput:
    user_id: int
    agent_id: str
    status: Literal["active", "non-active"]


@dataclass
class IntegrationOutput:
    integration_id: int
    platform_id: int
    api_key: str


class ApiIntegration(BaseUseCase[ApiIntegrationInput, IntegrationOutput]):
    def __init__(
        self,
        generate_api_key_usecase: GenerateApiKey,
        create_integration_usecase: CreateIntegration,
    ):
        self.generate_api_key = generate_api_key_usecase
        self.create_integration = create_integration_usecase

    async def execute(
        self, input_data: ApiIntegrationInput
    ) -> UseCaseResult[IntegrationOutput]:
        try:
            # Check integration
            integration = await self.create_integration.integration_repository.get_by_agent_and_platform(
                input_data.agent_id, "api"
            )

            if integration:
                return UseCaseResult.error_result(
                    "Integration is already exist", IntegrationIsAlreadyExist()
                )

            generate_api_key = await self.generate_api_key.execute(
                GenerateApiKeyInput(
                    user_id=input_data.user_id,
                    agent_id=input_data.agent_id,
                )
            )

            if not generate_api_key.is_success():
                return self._return_exception(generate_api_key)

            get_api_key_data = generate_api_key.get_data()
            if get_api_key_data is None:
                return UseCaseResult.error_result(
                    "Generate api key is not returned",
                    RuntimeError("Generate api key is not returned"),
                )
            new_integration = await self.create_integration.execute(
                CreateIntegrationInput(
                    input_data.agent_id,
                    "api",
                    input_data.status,
                    get_api_key_data.api_key,
                )
            )

            if not new_integration.is_success():
                return self._return_exception(new_integration)

            new_integration_data = new_integration.get_data()
            if new_integration_data is None:
                return UseCaseResult.error_result(
                    "New integration use case is not returned",
                    RuntimeError("New integration use case is not returned"),
                )

            return UseCaseResult.success_result(
                IntegrationOutput(
                    new_integration_data.integration_id,
                    new_integration_data.platform_id,
                    get_api_key_data.api_key,
                )
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while create api integration: {str(e)}", e
            )
