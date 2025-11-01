"""
Use case for getting user agents with statistics.
"""

from dataclasses import dataclass
from typing import Any, Dict

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository

from .calculate_agent_stats_use_case import (
    CalculateAgentStatsUseCase,
    CalculateStatsInput,
)
from .format_agent_data_use_case import FormatAgentDataInput, FormatAgentDataUseCase


@dataclass
class GetUserAgentsInput:
    """Input data for getting user agents."""

    user_id: int


@dataclass
class GetUserAgentsOutput:
    """Output data for user agents with statistics."""

    user_agents: list
    stats: Dict[str, Any]


class GetUserAgentsUseCase(BaseUseCase[GetUserAgentsInput, GetUserAgentsOutput]):
    """
    Use case for getting user agents with statistics.

    This use case orchestrates the retrieval of user agents and calculation
    of their statistics by coordinating multiple other use cases.
    """

    def __init__(
        self,
        agent_repository: IAgentRepository,
        format_agent_data_use_case: FormatAgentDataUseCase,
        calculate_stats_use_case: CalculateAgentStatsUseCase,
    ):
        self.agent_repository = agent_repository
        self.format_agent_data_use_case = format_agent_data_use_case
        self.calculate_stats_use_case = calculate_stats_use_case

    def validate_input(self, input_data: GetUserAgentsInput) -> UseCaseResult[None]:
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
        self, input_data: GetUserAgentsInput
    ) -> UseCaseResult[GetUserAgentsOutput]:
        """
        Get user agents with statistics.

        Args:
            input_data: Input containing user ID

        Returns:
            UseCaseResult containing user agents and statistics
        """
        try:
            # 1. Get agents with integrations (infrastructure)
            agents = await self.agent_repository.get_user_agents_with_integrations(
                input_data.user_id
            )

            # 2. Format agent data (business logic via use case)
            format_result = await self.format_agent_data_use_case.execute(
                FormatAgentDataInput(agents=agents)
            )

            if format_result.is_error():
                error_msg = format_result.get_error() or "Failed to format agent data"
                return UseCaseResult.error_result(error_msg)

            # 3. Get user with agents for statistics (infrastructure)
            user_with_agents = (
                await self.agent_repository.get_user_with_agents_for_statistics(
                    input_data.user_id
                )
            )

            # 4. Calculate statistics (business logic via use case)
            if not user_with_agents or not user_with_agents.agents:
                stats = {
                    "total_agents": 0,
                    "active_agents": 0,
                    "total_interactions": 0,
                    "total_tokens": 0,
                    "avg_response_time": 0.0,
                    "success_rate": 0.0,
                }
            else:
                stats_result = await self.calculate_stats_use_case.execute(
                    CalculateStatsInput(agents=user_with_agents.agents)
                )

                if stats_result.is_error():
                    error_msg = (
                        stats_result.get_error() or "Failed to calculate statistics"
                    )
                    return UseCaseResult.error_result(error_msg)

                if not stats_result.data:
                    return UseCaseResult.error_result("No statistics data returned")

                stats = stats_result.data.stats

            if not format_result.data:
                return UseCaseResult.error_result("No formatted agent data returned")

            return UseCaseResult.success_result(
                GetUserAgentsOutput(
                    user_agents=format_result.data.formatted_agents, stats=stats
                )
            )

        except Exception as e:
            return UseCaseResult.error_result(f"Failed to get user agents: {str(e)}")
