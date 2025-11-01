"""
Use case for deleting an agent.
"""

from dataclasses import dataclass

from src.app.validators.agent_schema import BaseAgentSchema
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository


@dataclass
class DeleteAgentInput:
    """Input data for deleting an agent."""

    agent_id: str


@dataclass
class DeleteAgentOutput:
    """Output data for deleted agent."""

    agent: BaseAgentSchema


class DeleteAgentUseCase(BaseUseCase[DeleteAgentInput, DeleteAgentOutput]):
    """
    Use case for deleting an agent.

    This use case handles the business logic for deleting an agent
    and returning the deleted agent information.
    """

    def __init__(self, agent_repository: IAgentRepository):
        self.agent_repository = agent_repository

    def validate_input(self, input_data: DeleteAgentInput) -> UseCaseResult[None]:
        """Validate input data."""
        if not hasattr(input_data, "agent_id"):
            return UseCaseResult.validation_error("agent_id", "Agent ID is required")

        if not isinstance(input_data.agent_id, str):
            return UseCaseResult.validation_error(
                "agent_id", "Agent ID must be a string"
            )

        if not input_data.agent_id.strip():
            return UseCaseResult.validation_error(
                "agent_id", "Agent ID cannot be empty"
            )

        return UseCaseResult.success_result(None)

    async def execute(
        self, input_data: DeleteAgentInput
    ) -> UseCaseResult[DeleteAgentOutput]:
        """
        Delete an agent.

        Args:
            input_data: Input containing agent ID

        Returns:
            UseCaseResult containing deleted agent information
        """
        try:
            # Delete agent from repository
            deleted_agent = await self.agent_repository.delete_agent_by_id(
                input_data.agent_id
            )

            if not deleted_agent:
                return UseCaseResult.not_found_error("Agent", input_data.agent_id)

            # Convert to schema
            agent_schema = BaseAgentSchema(
                id=deleted_agent.id,
                name=deleted_agent.name,
                avatar=deleted_agent.avatar,
                model=deleted_agent.model,
                role=deleted_agent.role,
                description=deleted_agent.description,
                status=deleted_agent.status,
                base_prompt=deleted_agent.base_prompt,
                short_term_memory=deleted_agent.short_term_memory,
                long_term_memory=deleted_agent.long_term_memory,
                tone=deleted_agent.tone,
                created_at=deleted_agent.created_at,
            )

            return UseCaseResult.success_result(DeleteAgentOutput(agent=agent_schema))

        except Exception as e:
            return UseCaseResult.error_result(f"Failed to delete agent: {str(e)}", e)
