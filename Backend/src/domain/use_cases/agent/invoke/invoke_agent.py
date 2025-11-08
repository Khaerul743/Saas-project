from dataclasses import dataclass
from typing import Literal

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.ai.agents import BaseAgent, BaseAgentStateModel

from .. import (
    CreateHistoryMessage,
    CreateHistoryMessageInput,
    CreateMetadata,
    CreateMetadataInput,
    CreateUserAgent,
    CreateUserAgentInput,
)


@dataclass
class InvokeAgentInput:
    agent_id: str
    unique_id: str
    username: str
    user_platform: Literal["telegram", "whatsapp", "api"]
    state_input: BaseAgentStateModel


@dataclass
class InvokeAgentOutput:
    user_message: str
    response: str
    total_tokens: int | float
    response_time: int | float


class InvokeAgent(BaseUseCase[InvokeAgentInput, InvokeAgentOutput]):
    def __init__(
        self,
        create_user_agent: CreateUserAgent,
        create_history_message: CreateHistoryMessage,
        create_metadata: CreateMetadata,
        agent: BaseAgent,
    ):
        self.create_user_agent = create_user_agent
        self.create_history_message = create_history_message
        self.create_metadata = create_metadata
        self.agent = agent

    async def execute(
        self, input_data: InvokeAgentInput
    ) -> UseCaseResult[InvokeAgentOutput]:
        try:
            # Create user agent
            new_user_agent = await self.create_user_agent.execute(
                CreateUserAgentInput(
                    input_data.agent_id,
                    input_data.unique_id,
                    input_data.username,
                    input_data.user_platform,
                )
            )
            if new_user_agent.is_success():
                return self._return_exception(new_user_agent)

            user_agent_data = new_user_agent.get_data()
            if not user_agent_data:
                return UseCaseResult.error_result(
                    "User agent data is empty", RuntimeError("User agent data is empty")
                )

            user_agent_id = user_agent_data.id

            self.agent.execute(input_data.state_input, user_agent_id)

            # get agent response
            response = self.agent.get_response()

            if response is None:
                return UseCaseResult.error_result(
                    "The agent did not response",
                    RuntimeError("The agent did not response"),
                )

            # get agent token usage
            total_tokens = self.agent.get_response_time()

            # get agent response time
            response_time = self.agent.get_response_time()

            # get agent llm model
            llm_model = self.agent.get_llm_model()

            # Save history message
            new_history_message = await self.create_history_message.execute(
                CreateHistoryMessageInput(
                    user_agent_id, input_data.state_input.user_message, response
                )
            )
            if not new_history_message:
                return self._return_exception(new_history_message)

            history_message_data = new_history_message.get_data()
            if not history_message_data:
                return UseCaseResult.error_result(
                    "History message data is empty",
                    RuntimeError("History message data is empty"),
                )

            # Create message metadata
            new_metadata = await self.create_metadata.execute(
                CreateMetadataInput(
                    history_message_data.id, total_tokens, response_time, llm_model
                )
            )
            if not new_metadata:
                return self._return_exception(new_metadata)

            return UseCaseResult.success_result(
                InvokeAgentOutput(
                    input_data.state_input.user_message,
                    response,
                    total_tokens,
                    response_time,
                )
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while invoked agent: {str(e)}", e
            )
