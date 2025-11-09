from dataclasses import dataclass
from typing import List, Optional

from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.models.agent_entity import Agent
from src.domain.models.user_entity import User
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository, UserRepositoryInterface


@dataclass
class GetDashboardOverviewInput:
    user_id: int


@dataclass
class DashboardOverviewOutput:
    token_usage: int
    total_conversations: int
    active_agents: int
    average_response_time: float
    success_rate: float


class GetDashboardOverview(BaseUseCase[GetDashboardOverviewInput, DashboardOverviewOutput]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        agent_repository: IAgentRepository,
    ):
        self.user_repository = user_repository
        self.agent_repository = agent_repository

    def _calculate_dashboard_overview(
        self, agents: List[Agent]
    ) -> DashboardOverviewOutput:
        """
        Calculate dashboard overview statistics from a list of agents.

        Args:
            agents: List of Agent objects with loaded relationships

        Returns:
            DashboardOverviewOutput containing dashboard statistics
        """
        total_tokens = 0
        total_conversations = 0
        active_agents = 0
        response_times: List[float] = []
        success_count = 0

        for agent in agents:
            if agent.status == "active":
                active_agents += 1

            for ua in agent.user_agents:
                for history in ua.history_messages:
                    total_conversations += 1
                    metadata = history.message_metadata
                    if metadata:
                        total_tokens += metadata.total_tokens or 0
                        if metadata.response_time is not None:
                            response_times.append(metadata.response_time)
                        if metadata.is_success:
                            success_count += 1

        avg_response_time = (
            round(sum(response_times) / len(response_times), 2) if response_times else 0.0
        )
        success_rate = (
            round((success_count / total_conversations) * 100, 2)
            if total_conversations > 0
            else 0.0
        )

        return DashboardOverviewOutput(
            token_usage=total_tokens,
            total_conversations=total_conversations,
            active_agents=active_agents,
            average_response_time=avg_response_time,
            success_rate=success_rate,
        )

    def _get_default_dashboard_response(self) -> DashboardOverviewOutput:
        """
        Get default dashboard response when no agents are found.

        Returns:
            Default dashboard statistics
        """
        return DashboardOverviewOutput(
            token_usage=0,
            total_conversations=0,
            active_agents=0,
            average_response_time=0.0,
            success_rate=0.0,
        )

    async def execute(
        self, input_data: GetDashboardOverviewInput
    ) -> UseCaseResult[DashboardOverviewOutput]:
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(input_data.user_id)
            if not user:
                return UseCaseResult.error_result(
                    "User not found",
                    UserNotFoundException(input_data.user_id),
                    "USER_NOT_FOUND",
                )

            # Get user with agents for statistics
            user_with_agents = (
                await self.agent_repository.get_user_with_agents_for_statistics(
                    input_data.user_id
                )
            )

            if not user_with_agents or not user_with_agents.agents:
                # Return default response when no agents found
                return UseCaseResult.success_result(
                    self._get_default_dashboard_response()
                )

            # Calculate dashboard overview
            overview = self._calculate_dashboard_overview(user_with_agents.agents)

            return UseCaseResult.success_result(overview)

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting dashboard overview: {str(e)}", e
            )

