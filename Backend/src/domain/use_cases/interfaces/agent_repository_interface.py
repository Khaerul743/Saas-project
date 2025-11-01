"""
Repository interface for Agent domain operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.domain.models.agent_entity import Agent
from src.domain.models.user_entity import User


class IAgentRepository(ABC):
    """
    Interface for Agent repository operations.
    This interface defines the contract for data access operations related to agents.
    """

    @abstractmethod
    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by its ID.

        Args:
            agent_id: The unique identifier of the agent

        Returns:
            Agent entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_agents_paginated(
        self, offset: int, limit: int
    ) -> Tuple[List[Agent], int]:
        """
        Get agents with pagination.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (agents list, total count)
        """
        pass

    @abstractmethod
    async def get_agents_with_details_by_user_id(self, user_id: int) -> List[Agent]:
        """
        Get agents with all relationships and statistics for a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of agents with their relationships loaded
        """
        pass

    @abstractmethod
    async def get_user_agents_with_integrations(self, user_id: int) -> List[Agent]:
        """
        Get agents with integrations for a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of agents with their integrations loaded
        """
        pass

    @abstractmethod
    async def get_user_with_agents_for_statistics(self, user_id: int) -> Optional[User]:
        """
        Get user with agents for statistics calculation.

        Args:
            user_id: The ID of the user

        Returns:
            User entity with agents and their relationships loaded, None if not found
        """
        pass

    @abstractmethod
    async def delete_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Delete an agent by its ID.

        Args:
            agent_id: The unique identifier of the agent

        Returns:
            The deleted agent entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_agent(self, user_id: int, agent_data: dict) -> Agent:
        """
        Create a new agent.

        Args:
            agent_data: Dictionary containing agent data

        Returns:
            The created agent entity
        """
        pass

    @abstractmethod
    async def update_agent(self, agent_id: str, agent_data: dict) -> Optional[Agent]:
        """
        Update an existing agent.

        Args:
            agent_id: The unique identifier of the agent
            agent_data: Dictionary containing updated agent data

        Returns:
            The updated agent entity if found, None otherwise
        """
        pass
