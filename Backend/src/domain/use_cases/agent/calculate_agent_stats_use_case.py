"""
Use case for calculating agent statistics.
"""
from typing import List, Dict, Any
from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult


@dataclass
class CalculateStatsInput:
    """Input data for calculating statistics."""
    agents: List[Any]


@dataclass
class CalculateStatsOutput:
    """Output data for calculated statistics."""
    stats: Dict[str, Any]


class CalculateAgentStatsUseCase(BaseUseCase[CalculateStatsInput, CalculateStatsOutput]):
    """
    Use case for calculating agent statistics from user agents.
    
    This use case handles the business logic for calculating various
    statistics related to agent performance and usage.
    """
    
    def validate_input(self, input_data: CalculateStatsInput) -> UseCaseResult[None]:
        """Validate input data."""
        if not hasattr(input_data, 'agents'):
            return UseCaseResult.validation_error("agents", "Agents list is required")
        
        if not isinstance(input_data.agents, list):
            return UseCaseResult.validation_error("agents", "Agents must be a list")
        
        return UseCaseResult.success_result(None)
    
    async def execute(self, input_data: CalculateStatsInput) -> UseCaseResult[CalculateStatsOutput]:
        """
        Calculate agent statistics.
        
        Args:
            input_data: Input containing list of agent entities
            
        Returns:
            UseCaseResult containing calculated statistics
        """
        try:
            if not input_data.agents:
                stats = self._get_default_stats()
            else:
                stats = self._calculate_statistics(input_data.agents)
            
            return UseCaseResult.success_result(CalculateStatsOutput(stats=stats))
            
        except Exception as e:
            return UseCaseResult.error_result(f"Failed to calculate statistics: {str(e)}")
    
    def _calculate_statistics(self, agents: List[Any]) -> Dict[str, Any]:
        """
        Calculate statistics from agent data.
        
        Args:
            agents: List of agent entities
            
        Returns:
            Dictionary containing calculated statistics
        """
        total_agents = len(agents)
        active_agents = sum(
            1 for agent in agents if getattr(agent, "status", None) == "active"
        )
        
        # Calculate total interactions and tokens
        total_interactions = 0
        total_tokens = 0
        total_response_time = 0
        successful_interactions = 0
        
        for agent in agents:
            if hasattr(agent, "user_agents") and agent.user_agents:
                for user_agent in agent.user_agents:
                    if (
                        hasattr(user_agent, "history_messages")
                        and user_agent.history_messages
                    ):
                        for message in user_agent.history_messages:
                            if (
                                hasattr(message, "message_metadata")
                                and message.message_metadata
                            ):
                                metadata = message.message_metadata
                                total_interactions += 1
                                
                                if (
                                    hasattr(metadata, "total_tokens")
                                    and metadata.total_tokens
                                ):
                                    total_tokens += metadata.total_tokens
                                
                                if (
                                    hasattr(metadata, "response_time")
                                    and metadata.response_time
                                ):
                                    total_response_time += metadata.response_time
                                
                                if hasattr(metadata, "is_success") and metadata.is_success:
                                    successful_interactions += 1
        
        # Calculate averages
        avg_response_time = (
            total_response_time / total_interactions if total_interactions > 0 else 0
        )
        success_rate = (
            (successful_interactions / total_interactions * 100)
            if total_interactions > 0
            else 0
        )
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_interactions": total_interactions,
            "total_tokens": total_tokens,
            "avg_response_time": round(avg_response_time, 2),
            "success_rate": round(success_rate, 2),
        }
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """
        Get default statistics when no agents are found.
        
        Returns:
            Dictionary containing default statistics
        """
        return {
            "total_agents": 0,
            "active_agents": 0,
            "total_interactions": 0,
            "total_tokens": 0,
            "avg_response_time": 0.0,
            "success_rate": 0.0,
        }
