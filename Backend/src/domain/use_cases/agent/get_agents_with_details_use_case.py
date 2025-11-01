"""
Use case for getting agents with details and statistics.
"""

from typing import List
from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository
from src.app.validators.agent_schema import AgentDetailSchema


@dataclass
class GetAgentsWithDetailsInput:
    """Input data for getting agents with details."""

    user_id: int


@dataclass
class GetAgentsWithDetailsOutput:
    """Output data for agents with details."""

    agents: List[AgentDetailSchema]


class GetAgentsWithDetailsUseCase(
    BaseUseCase[GetAgentsWithDetailsInput, GetAgentsWithDetailsOutput]
):
    """
    Use case for getting agents with details and statistics.

    This use case handles the retrieval and formatting of agent details
    including platform information, API keys, and conversation statistics.
    """

    def __init__(self, agent_repository: IAgentRepository):
        self.agent_repository: IAgentRepository = agent_repository

    def validate_input(
        self, input_data: GetAgentsWithDetailsInput
    ) -> UseCaseResult[None]:
        """Validate input data."""
        if not hasattr(input_data, "user_id"):
            return UseCaseResult.validation_error("user_id", "User ID is required")

        if not isinstance(input_data.user_id, int):
            return UseCaseResult.validation_error(
                "user_id", "User ID must be an integer"
            )

        if input_data.user_id <= 0:
            return UseCaseResult.validation_error("user_id", "User ID must be positive")

        return UseCaseResult.success_result(None)

    async def execute(
        self, input_data: GetAgentsWithDetailsInput
    ) -> UseCaseResult[GetAgentsWithDetailsOutput]:
        """
        Get agents with details and statistics.

        Args:
            input_data: Input containing user ID

        Returns:
            UseCaseResult containing agents with details
        """
        try:
            # Get agents with all relationships
            agents = await self.agent_repository.get_agents_with_details_by_user_id(
                input_data.user_id
            )

            if not agents:
                return UseCaseResult.success_result(
                    GetAgentsWithDetailsOutput(agents=[])
                )

            # Format agents with details
            agents_with_details = []
            for agent in agents:
                # Get all history from all user_agents of this agent
                all_histories = []
                for ua in agent.user_agents:
                    all_histories.extend(ua.history_messages)

                # Total conversations
                total_conversations = len(all_histories)

                # Average response time
                response_times = [
                    h.message_metadata.response_time
                    for h in all_histories
                    if h.message_metadata is not None
                ]
                avg_response_time = (
                    sum(response_times) / len(response_times) if response_times else 0
                )

                # Get platform and API key from integrations (prioritize active integrations)
                platform = None
                api_key = None
                if agent.integrations:
                    # First try to find an active integration
                    active_integration = next(
                        (
                            integration
                            for integration in agent.integrations
                            if integration.status == "active"
                        ),
                        None,
                    )
                    if active_integration:
                        platform = active_integration.platform
                        # Get API key from platform integration if available
                        if active_integration.platform_config:
                            api_key = active_integration.platform_config.api_key
                    else:
                        # If no active integration, take the first one
                        first_integration = agent.integrations[0]
                        platform = first_integration.platform
                        # Get API key from platform integration if available
                        if first_integration.platform_config:
                            api_key = first_integration.platform_config.api_key

                agents_with_details.append(
                    AgentDetailSchema(
                        id=agent.id,
                        avatar=agent.avatar,
                        name=agent.name,
                        model=agent.model,
                        role=agent.role,
                        status=agent.status,
                        description=agent.description,
                        base_prompt=agent.base_prompt,
                        short_term_memory=agent.short_term_memory,
                        long_term_memory=agent.long_term_memory,
                        tone=agent.tone,
                        created_at=agent.created_at,
                        platform=platform,
                        api_key=api_key,
                        total_conversations=total_conversations,
                        avg_response_time=round(avg_response_time, 2),
                    )
                )

            return UseCaseResult.success_result(
                GetAgentsWithDetailsOutput(agents=agents_with_details)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Failed to get agents with details: {str(e)}"
            )
