from dataclasses import dataclass
from typing import List

from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository, UserRepositoryInterface


@dataclass
class GetTotalTokensPerAgentInput:
    user_id: int


@dataclass
class AgentTokenItem:
    agent_id: str
    agent_name: str
    total_tokens: int


@dataclass
class GetTotalTokensPerAgentOutput:
    agents: List[AgentTokenItem]


class GetTotalTokensPerAgent(BaseUseCase[GetTotalTokensPerAgentInput, GetTotalTokensPerAgentOutput]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        agent_repository: IAgentRepository,
    ):
        self.user_repository = user_repository
        self.agent_repository = agent_repository

    def _format_total_tokens_per_agent_data(self, results: List) -> List[AgentTokenItem]:
        """
        Format total tokens per agent data from database query results.

        Args:
            results: Raw query results from database

        Returns:
            List of AgentTokenItem containing agent_id, agent_name, and total_tokens
        """
        agents_tokens = [
            AgentTokenItem(
                agent_id=str(r.agent_id),
                agent_name=str(r.agent_name),
                total_tokens=int(r.total_tokens or 0),
            )
            for r in results
        ]
        return agents_tokens

    async def execute(
        self, input_data: GetTotalTokensPerAgentInput
    ) -> UseCaseResult[GetTotalTokensPerAgentOutput]:
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(input_data.user_id)
            if not user:
                return UseCaseResult.error_result(
                    "User not found",
                    UserNotFoundException(input_data.user_id),
                    "USER_NOT_FOUND",
                )

            # Get total tokens per agent from repository
            results = await self.agent_repository.get_total_tokens_per_agent(
                user_id=input_data.user_id
            )

            # Format results
            agents_tokens = self._format_total_tokens_per_agent_data(list(results))

            return UseCaseResult.success_result(
                GetTotalTokensPerAgentOutput(agents=agents_tokens)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting total tokens per agent: {str(e)}", e
            )

