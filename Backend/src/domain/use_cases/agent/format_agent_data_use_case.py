"""
Use case for formatting agent data for API response.
"""
from typing import List, Dict, Any
from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult


@dataclass
class FormatAgentDataInput:
    """Input data for formatting agent data."""
    agents: List[Any]


@dataclass
class FormatAgentDataOutput:
    """Output data for formatted agent data."""
    formatted_agents: List[Dict[str, Any]]


class FormatAgentDataUseCase(BaseUseCase[FormatAgentDataInput, FormatAgentDataOutput]):
    """
    Use case for formatting agent data into API response format.
    
    This use case handles the transformation of agent entities into
    the format expected by the API consumers.
    """
    
    def validate_input(self, input_data: FormatAgentDataInput) -> UseCaseResult[None]:
        """Validate input data."""
        if not hasattr(input_data, 'agents'):
            return UseCaseResult.validation_error("agents", "Agents list is required")
        
        if not isinstance(input_data.agents, list):
            return UseCaseResult.validation_error("agents", "Agents must be a list")
        
        return UseCaseResult.success_result(None)
    
    async def execute(self, input_data: FormatAgentDataInput) -> UseCaseResult[FormatAgentDataOutput]:
        """
        Format agent data for API response.
        
        Args:
            input_data: Input containing list of agent entities
            
        Returns:
            UseCaseResult containing formatted agent data
        """
        try:
            formatted_agents = []
            
            for agent in input_data.agents:
                agent_data = {
                    "id": agent.id,
                    "name": agent.name,
                    "avatar": agent.avatar,
                    "model": agent.model,
                    "role": agent.role,
                    "description": agent.description,
                    "status": agent.status,
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                }
                
                # Add integrations if available
                if hasattr(agent, "integrations") and agent.integrations:
                    agent_data["integrations"] = [
                        {
                            "id": integration.id,
                            "platform": integration.platform,
                            "status": integration.status,
                        }
                        for integration in agent.integrations
                    ]
                
                formatted_agents.append(agent_data)
            
            return UseCaseResult.success_result(
                FormatAgentDataOutput(formatted_agents=formatted_agents)
            )
            
        except Exception as e:
            return UseCaseResult.error_result(f"Failed to format agent data: {str(e)}")
