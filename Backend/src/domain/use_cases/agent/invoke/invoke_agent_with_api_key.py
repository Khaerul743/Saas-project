from dataclasses import dataclass

from src.core.exceptions.agent_exceptions import InvalidApiKeyException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IApiKeyRepository
from src.infrastructure.ai.agents import BaseAgentStateModel

from .invoke_agent import InvokeAgent, InvokeAgentInput, InvokeAgentOutput


@dataclass
class InvokeAgentApiInput:
    agent_id: str
    unique_id: str
    username: str
    message: str
    api_key: str
    state: BaseAgentStateModel


class InvokeAgentApi(BaseUseCase[InvokeAgentApiInput, InvokeAgentOutput]):
    def __init__(
        self,
        api_key_repository: IApiKeyRepository,
        invoke_agent_usecase: InvokeAgent,
    ):
        self.api_key_repository = api_key_repository
        self.invoke_agent = invoke_agent_usecase

    async def execute(
        self, input_data: InvokeAgentApiInput
    ) -> UseCaseResult[InvokeAgentOutput]:
        try:
            # Validate api key
            validate_api_key = await self.api_key_repository.get_active_api_key(
                input_data.agent_id, input_data.api_key
            )
            if validate_api_key is None:
                raise InvalidApiKeyException(input_data.api_key)

            invoke_agent = await self.invoke_agent.execute(
                InvokeAgentInput(
                    input_data.agent_id,
                    input_data.unique_id,
                    input_data.username,
                    "api",
                    input_data.state,
                )
            )

            if not invoke_agent.is_success():
                return self._return_exception(invoke_agent)

            response_data = invoke_agent.get_data()
            if response_data is None:
                return UseCaseResult.error_result(
                    "Invoke agent is not returned data",
                    RuntimeError("Invoke agent is not returned data"),
                )

            return UseCaseResult.success_result(response_data)

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while invoke agent with apikey: {str(e)}", e
            )
