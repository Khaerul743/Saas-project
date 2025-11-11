from dataclasses import dataclass
from typing import Literal

from src.core.exceptions.agent_exceptions import AgentNotFoundException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import (
    IAgentRepository,
    IStorageAgentObj,
    IUserAgentRepository,
)
from src.infrastructure.ai.agents import BaseAgentStateModel
from src.infrastructure.data import AgentManager

from ..history_message import (
    CreateHistoryMessage,
    CreateHistoryMessageInput,
    CreateMetadata,
    CreateMetadataInput,
)
from ..initial_agent_again import InitialAgentAgain, InitialAgentAgainInput
from ..user_agent import (
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
        agent_repository: IAgentRepository,
        user_agent_repository: IUserAgentRepository,
        create_user_agent: CreateUserAgent,
        create_history_message: CreateHistoryMessage,
        create_metadata: CreateMetadata,
        agent_manager: AgentManager,
        storage_agent_obj: IStorageAgentObj,
        initial_agent_again: InitialAgentAgain,
    ):
        self.agent_repository = agent_repository
        self.user_agent_repository = user_agent_repository
        self.create_user_agent = create_user_agent
        self.create_history_message = create_history_message
        self.create_metadata = create_metadata
        self.agent_manager = agent_manager
        self.store_agent_obj = storage_agent_obj
        self.initial_agent_again = initial_agent_again

    async def execute(
        self, input_data: InvokeAgentInput
    ) -> UseCaseResult[InvokeAgentOutput]:
        try:
            # Is user agent exist

            user_agent_id = input_data.agent_id + input_data.unique_id
            user_agent_data = await self.user_agent_repository.get_user_agent_by_id(
                user_agent_id
            )
            if not user_agent_data:
                print("USER AGENT KAGA ADA")
                # Create user agent
                new_user_agent = await self.create_user_agent.execute(
                    CreateUserAgentInput(
                        input_data.agent_id,
                        input_data.unique_id,
                        input_data.username,
                        input_data.user_platform,
                    )
                )

                if not new_user_agent.is_success():
                    return self._return_exception(new_user_agent)

                user_agent_data = new_user_agent.get_data()
                if not user_agent_data:
                    return UseCaseResult.error_result(
                        "User agent data is empty",
                        RuntimeError("User agent data is empty"),
                    )

                user_agent_id = user_agent_data.id

            # Get agent in agent manager
            agent = self.agent_manager.get_agent_in_memory(input_data.agent_id)
            print(
                f"ALL AGENTS IN MEMORY: {self.agent_manager.get_all_agents_in_memory()}"
            )
            if not agent:
                print("AGENT DOESNT EXISTTTT")
                # if agent doens't exist, get agent from storage obj
                get_agent_from_storage_obj = await self.store_agent_obj.get_agent(
                    input_data.agent_id
                )
                if not get_agent_from_storage_obj:
                    return UseCaseResult.error_result(
                        "Agent not found", AgentNotFoundException(input_data.agent_id)
                    )

                # Initial the agent again
                role = get_agent_from_storage_obj.get("role")
                if not role:
                    return UseCaseResult.error_result(
                        "Role agent obj is empty", ValueError("Role agent obj is empty")
                    )

                initial_agent = self.initial_agent_again.execute(
                    InitialAgentAgainInput(
                        input_data.agent_id, role, get_agent_from_storage_obj
                    )
                )
                if not initial_agent.is_success():
                    self._return_exception(initial_agent)

                get_agent = initial_agent.get_data()
                if not get_agent:
                    return UseCaseResult.error_result(
                        "Agent is empty", RuntimeError("Agent is empty")
                    )

                agent = get_agent.agent

            agent.execute(input_data.state_input, user_agent_id)

            # get agent response
            response = agent.get_response()

            if response is None:
                return UseCaseResult.error_result(
                    "The agent did not response",
                    RuntimeError("The agent did not response"),
                )

            # get agent token usage
            total_tokens = agent.get_token_usage()

            # get agent response time
            response_time = agent.get_response_time()

            # get agent llm model
            llm_model = agent.get_llm_model()

            # Save history message
            new_history_message = await self.create_history_message.execute(
                CreateHistoryMessageInput(
                    user_agent_id, input_data.state_input.user_message, response
                )
            )
            if not new_history_message.is_success():
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
            if not new_metadata.is_success():
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
