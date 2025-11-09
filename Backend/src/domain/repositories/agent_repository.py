from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from src.domain.models.agent_entity import Agent
from src.domain.models.history_entity import HistoryMessage
from src.domain.models.integration_entity import Integration
from src.domain.models.metadata_entity import Metadata
from src.domain.models.platform_entity import Platform
from src.domain.models.user_agent_entity import UserAgent
from src.domain.models.user_entity import User
from src.domain.use_cases.interfaces import IAgentRepository


class AgentRepository(IAgentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_agent_by_user_id(self, user_id: int, agent_id: str):
        query = select(Agent).where(Agent.user_id == user_id, Agent.id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_agent_by_id(self, agent_id: str):
        query = select(Agent).where(Agent.id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_agents_paginated(self, offset: int, limit: int):
        """
        Ambil daftar user dengan pagination (raw result).
        """

        stmt = (
            select(
                Agent.id,
                Agent.user_id,
                Agent.name,
                Agent.avatar,
                Agent.model,
                Agent.role,
                Agent.description,
                Agent.status,
                Agent.base_prompt,
                Agent.short_term_memory,
                Agent.long_term_memory,
                Agent.tone,
                Agent.created_at,
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        agents = result.all()  # raw sqlalchemy Row objects

        total_stmt = select(func.count()).select_from(Agent)
        total_result = await self.db.execute(total_stmt)
        total_agents = total_result.scalar_one()

        return agents, total_agents

    async def get_agents_with_details_by_user_id(self, user_id: int):
        """
        Get agents with all relationships and statistics for a specific user.
        """
        stmt = (
            select(Agent)
            .filter(Agent.user_id == user_id)
            .options(
                joinedload(Agent.user_agents)
                .joinedload(UserAgent.history_messages)
                .joinedload(HistoryMessage.message_metadata),
                joinedload(Agent.integrations).joinedload(Integration.platform_config),
            )
        )

        result = await self.db.execute(stmt)
        agents = result.unique().scalars().all()

        return agents

    async def delete_agent_by_id(self, agent_id: str):
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return None
        await self.db.delete(agent)
        await self.db.flush()
        return agent

    async def get_user_agents_with_integrations(self, user_id: int):
        """
        Get agents with integrations for a specific user.
        """
        stmt = (
            select(Agent)
            .filter(Agent.user_id == user_id)
            .options(
                joinedload(Agent.user_agents),
                joinedload(Agent.integrations),
            )
        )

        result = await self.db.execute(stmt)
        agents = result.unique().scalars().all()

        return agents

    async def get_user_with_agents_for_statistics(self, user_id: int):
        """
        Get user with agents for statistics calculation.
        """
        stmt = (
            select(User)
            .filter(User.id == user_id)
            .options(
                joinedload(User.agents)
                .load_only(Agent.id, Agent.status)
                .joinedload(Agent.user_agents)
                .load_only(UserAgent.id, UserAgent.created_at)
                .joinedload(UserAgent.history_messages)
                .load_only(HistoryMessage.id)
                .joinedload(HistoryMessage.message_metadata)
                .load_only(
                    Metadata.total_tokens,
                    Metadata.response_time,
                    Metadata.is_success,
                )
            )
        )

        result = await self.db.execute(stmt)
        user = result.unique().scalar_one_or_none()

        return user

    async def create_agent(self, user_id: int, agent_data: dict) -> Agent:
        """
        Create a new agent.

        Args:
            agent_data: Dictionary containing agent data

        Returns:
            The created agent entity
        """
        agent = Agent(
            id=agent_data.get("id"),
            user_id=user_id,
            name=agent_data.get("name"),
            avatar=agent_data.get("avatar"),
            model=agent_data.get("model"),
            role=agent_data.get("role"),
            description=agent_data.get("description"),
            base_prompt=agent_data.get("base_prompt"),
            tone=agent_data.get("tone"),
            short_term_memory=agent_data.get("short_term_memory"),
            long_term_memory=agent_data.get("long_term_memory"),
            status=agent_data.get("status"),
        )

        self.db.add(agent)
        await self.db.flush()
        await self.db.refresh(agent)
        return agent

    async def update_agent(self, agent_id: str, agent_data: dict) -> Optional[Agent]:
        """
        Update an existing agent.

        Args:
            agent_id: The unique identifier of the agent
            agent_data: Dictionary containing updated agent data

        Returns:
            The updated agent entity if found, None otherwise
        """
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return None

        for key, value in agent_data.items():
            if hasattr(agent, key):
                setattr(agent, key, value)

        await self.db.flush()
        await self.db.refresh(agent)
        return agent
