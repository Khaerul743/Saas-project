"""
Use case for getting all agents with pagination.
"""
from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository
from src.app.validators.agent_schema import AgentPaginate, AgentPaginateOut


@dataclass
class GetAllAgentsInput:
    """Input data for getting all agents."""
    page: int
    limit: int


@dataclass
class GetAllAgentsOutput:
    """Output data for all agents."""
    agents: AgentPaginateOut


class GetAllAgentsUseCase(BaseUseCase[GetAllAgentsInput, GetAllAgentsOutput]):
    """
    Use case for getting all agents with pagination.
    
    This use case handles the retrieval of all agents with pagination
    and formatting them for API response.
    """
    
    def __init__(self, agent_repository: IAgentRepository):
        self.agent_repository = agent_repository
    
    def validate_input(self, input_data: GetAllAgentsInput) -> UseCaseResult[None]:
        """Validate input data."""
        if not hasattr(input_data, 'page'):
            return UseCaseResult.validation_error("page", "Page is required")
        
        if not hasattr(input_data, 'limit'):
            return UseCaseResult.validation_error("limit", "Limit is required")
        
        if not isinstance(input_data.page, int):
            return UseCaseResult.validation_error("page", "Page must be an integer")
        
        if not isinstance(input_data.limit, int):
            return UseCaseResult.validation_error("limit", "Limit must be an integer")
        
        if input_data.page < 1:
            return UseCaseResult.validation_error("page", "Page must be greater than 0")
        
        if input_data.limit < 1:
            return UseCaseResult.validation_error("limit", "Limit must be greater than 0")
        
        if input_data.limit > 100:
            return UseCaseResult.validation_error("limit", "Limit cannot exceed 100")
        
        return UseCaseResult.success_result(None)
    
    async def execute(self, input_data: GetAllAgentsInput) -> UseCaseResult[GetAllAgentsOutput]:
        """
        Get all agents with pagination.
        
        Args:
            input_data: Input containing page and limit
            
        Returns:
            UseCaseResult containing paginated agents
        """
        try:
            # Calculate offset
            offset = (input_data.page - 1) * input_data.limit
            
            # Get agents from repository
            agents, total = await self.agent_repository.get_agents_paginated(offset, input_data.limit)
            
            # Format agents
            data_agents = [
                AgentPaginate(
                    id=agent.id,
                    name=agent.name,
                    user_id=agent.user_id,
                    avatar=agent.avatar,
                    model=agent.model,
                    role=agent.role,
                    description=agent.description,
                    status=agent.status,
                    base_prompt=agent.base_prompt,
                    short_term_memory=agent.short_term_memory,
                    long_term_memory=agent.long_term_memory,
                    tone=agent.tone,
                    created_at=agent.created_at,
                )
                for agent in agents
            ]
            
            # Create paginated output
            agents_output = AgentPaginateOut(
                data_agents=data_agents,
                total=total,
                limit=input_data.limit,
                page=input_data.page
            )
            
            return UseCaseResult.success_result(
                GetAllAgentsOutput(agents=agents_output)
            )
            
        except Exception as e:
            return UseCaseResult.error_result(f"Failed to get all agents: {str(e)}")
