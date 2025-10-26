from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.agent_exceptions import AgentNotFoundException
from app.exceptions.database_exceptions import DatabaseException
from app.repository.agent_repository import AgentRepository
from app.schema.agent_schema import (
    AgentDetailSchema,
    AgentPaginate,
    AgentPaginateOut,
    AgentStatsSchema,
    BaseAgentSchema,
    UserAgentSchema,
)
from app.services import BaseService


class AgentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.agent_repo = AgentRepository(db)

    async def get_all_agents(self, page: int, limit: int) -> AgentPaginateOut:
        try:
            offset = (page - 1) * limit
            agents, total = await self.agent_repo.get_agents_paginated(offset, limit)
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
            self.log_context("admin getting all agents paginate")

            return AgentPaginateOut(
                data_agents=data_agents, total=total, limit=limit, page=page
            )
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting all agetns paginated", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("getting all agents", e)
            raise  # Re-raise exception

    async def get_agents_with_details_by_user_id(
        self, user_id: int
    ) -> list[AgentDetailSchema]:
        try:
            agents = await self.agent_repo.get_agents_with_details_by_user_id(user_id)

            if not agents:
                self.log_context(f"No agents found for user {user_id}")
                return []  # frontend gets empty array, not error

            # Format agents summary
            agents_summary = []
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

                agents_summary.append(
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

            self.log_context(f"Successfully retrieved agents for user {user_id}")
            return agents_summary

        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting agents with details", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("getting agents with details", e)
            raise

    async def delete_agent(self, agent_id: str) -> BaseAgentSchema:
        try:
            agent = await self.agent_repo.delete_agent_by_id(agent_id)
            if not agent:
                raise AgentNotFoundException(agent_id)
            self.log_context("Deleted agent")
            return BaseAgentSchema(
                id=agent.id,
                name=agent.name,
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
        except AgentNotFoundException as e:
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting agents with details", e)
            raise

    async def get_user_agents_with_statistics(self, user_id: int) -> dict:
        try:
            # Get agents with integrations
            agents = await self.agent_repo.get_user_agents_with_integrations(user_id)
            
            # Format user agents data
            formatted_agents = self._format_user_agents_data(agents)
            
            # Get user with agents for statistics
            user_with_agents = await self.agent_repo.get_user_with_agents_for_statistics(user_id)
            
            if not user_with_agents or not user_with_agents.agents:
                self.log_context(f"No agents found for user {user_id}")
                return {
                    "user_agents": formatted_agents, 
                    "stats": self._get_default_stats_response()
                }
            
            # Calculate statistics
            stats = self._calculate_agent_statistics(user_with_agents.agents)
            
            self.log_context(f"Fetched {len(formatted_agents)} user agents for user_id={user_id}")
            return {"user_agents": formatted_agents, "stats": stats}
            
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting user agents with statistics", e)
            raise
        except Exception as e:
            self.handle_unexpected_error("getting user agents with statistics", e)
            raise

    def _format_user_agents_data(self, agents) -> list:
        """
        Format user agents data for API response
        """
        result = []
        
        for agent in agents:
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
            
            result.append(agent_data)
        
        return result

    def _calculate_agent_statistics(self, agents) -> dict:
        """
        Calculate agent statistics from user agents
        """
        if not agents:
            return self._get_default_stats_response()
        
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

    def _get_default_stats_response(self) -> dict:
        """
        Get default statistics response when no agents found
        """
        return {
            "total_agents": 0,
            "active_agents": 0,
            "total_interactions": 0,
            "total_tokens": 0,
            "avg_response_time": 0.0,
            "success_rate": 0.0,
        }
