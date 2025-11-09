from typing import Literal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.agent_schema import (
    AgentDetailSchema,
    AgentPaginate,
    AgentPaginateOut,
    AgentStatsSchema,
    BaseAgentSchema,
    UserAgentSchema,
)
from src.core.exceptions.agent_exceptions import AgentNotFoundException
from src.core.exceptions.database_exceptions import DatabaseException
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.repositories.history_message_repository import HistoryMessageRepository
from src.domain.repositories.metadata_repository import MetadataRepository
from src.domain.repositories.user_agent_repository import UserAgentRepository
from src.domain.service import BaseService
from src.domain.use_cases.agent import (
    CalculateAgentStatsUseCase,
    CreateHistoryMessage,
    CreateMetadata,
    CreateUserAgent,
    DeleteAgentUseCase,
    FormatAgentDataUseCase,
    GetAgentsWithDetailsUseCase,
    GetAllAgentsUseCase,
    GetUserAgentsUseCase,
    InitialAgentAgain,
    InitialSimpleRagAgent,
    InvokeAgent,
    InvokeAgentInput,
    StoreAgentInMemory,
)
from src.infrastructure.ai.agents import BaseAgentStateModel
from src.infrastructure.data import agent_manager
from src.infrastructure.redis.redis_storage import RedisStorage


class AgentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.user_agent_repo = UserAgentRepository(db)
        self.history_message_repo = HistoryMessageRepository(db)
        self.metadata_repo = MetadataRepository(db)
        self.storage_agent_obj = RedisStorage()
        self.agent_manager = agent_manager

        # Initialize use cases
        self.format_agent_data_use_case = FormatAgentDataUseCase()
        self.calculate_stats_use_case = CalculateAgentStatsUseCase()
        self.get_all_agents_use_case = GetAllAgentsUseCase(self.agent_repo)
        self.get_agents_with_details_use_case = GetAgentsWithDetailsUseCase(
            self.agent_repo
        )
        self.get_user_agents_use_case = GetUserAgentsUseCase(
            self.agent_repo,
            self.format_agent_data_use_case,
            self.calculate_stats_use_case,
        )
        self.delete_agent_use_case = DeleteAgentUseCase(self.agent_repo)

        # Invoke agent
        self.store_agent_in_memory = StoreAgentInMemory(self.agent_manager)
        self.initial_simple_rag_agent = InitialSimpleRagAgent(
            self.store_agent_in_memory
        )
        self.create_user_agent = CreateUserAgent(self.user_agent_repo)
        self.create_history_message = CreateHistoryMessage(self.history_message_repo)
        self.create_metadata = CreateMetadata(self.metadata_repo)

        self.initial_agent_again = InitialAgentAgain(self.initial_simple_rag_agent)

        self.invoke_agent_use_case = InvokeAgent(
            self.agent_repo,
            self.create_user_agent,
            self.create_history_message,
            self.create_metadata,
            self.agent_manager,
            self.storage_agent_obj,
            self.initial_agent_again,
        )

    async def get_all_agents(self, page: int, limit: int) -> AgentPaginateOut:
        """Get all agents with pagination using use case."""
        try:
            from src.domain.use_cases.agent import GetAllAgentsInput

            result = await self.get_all_agents_use_case.execute(
                GetAllAgentsInput(page=page, limit=limit)
            )

            if result.is_error():
                raise Exception(result.get_error())

            if not result.data:
                raise Exception("No data returned from use case")

            self.log_context("admin getting all agents paginate")
            return result.data.agents

        except Exception as e:
            self.handle_unexpected_error("getting all agents", e)
            raise

    async def get_agents_with_details_by_user_id(
        self, user_id: int
    ) -> list[AgentDetailSchema]:
        """Get agents with details by user ID using use case."""
        try:
            from src.domain.use_cases.agent import GetAgentsWithDetailsInput

            result = await self.get_agents_with_details_use_case.execute(
                GetAgentsWithDetailsInput(user_id=user_id)
            )

            if result.is_error():
                raise Exception(result.get_error())

            if not result.data:
                raise Exception("No data returned from use case")

            self.log_context(f"Successfully retrieved agents for user {user_id}")
            return result.data.agents

        except Exception as e:
            self.handle_unexpected_error("getting agents with details", e)
            raise

    async def delete_agent(self, agent_id: str) -> BaseAgentSchema:
        """Delete agent using use case."""
        try:
            from src.domain.use_cases.agent import DeleteAgentInput

            result = await self.delete_agent_use_case.execute(
                DeleteAgentInput(agent_id=agent_id)
            )

            if result.is_error():
                if result.error_code == "NOT_FOUND":
                    raise AgentNotFoundException(agent_id)
                raise Exception(result.get_error())

            if not result.data:
                raise Exception("No data returned from use case")

            self.log_context("Deleted agent")
            await self.db.commit()
            return result.data.agent

        except AgentNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error("deleting agent", e)
            raise

    async def invoke_agent(
        self,
        agent_id: str,
        username: str,
        user_platform: Literal["telegram", "whatsapp", "api"],
        user_message: str,
    ):
        """
        Invoke an agent with user message.

        Args:
            agent_id: ID of the agent to invoke
            username: Username of the user invoking the agent
            user_platform: Platform where the user is invoking from
            user_message: Message from the user

        Returns:
            InvokeAgentOutput with response and metadata

        Raises:
            AgentNotFoundException: If agent is not found
            DatabaseException: If database operation fails
        """
        try:
            # Get current user ID for unique_id
            current_user_id = self.current_user_id()
            # Validate agent is exist
            get_agent = await self.agent_repo.get_agent_by_user_id(
                current_user_id, agent_id
            )

            if not get_agent:
                raise AgentNotFoundException(agent_id)

            unique_id = str(current_user_id) if current_user_id else username

            invoked_agent = await self.invoke_agent_use_case.execute(
                InvokeAgentInput(
                    current_user_id,
                    agent_id,
                    unique_id,
                    username,
                    user_platform,
                    BaseAgentStateModel(messages=[], user_message=user_message),
                )
            )

            if not invoked_agent:
                self.logger.warning(
                    f"Agent invocation failed: {invoked_agent.get_error()}"
                )
                get_exception = invoked_agent.get_exception()
                if get_exception:
                    raise get_exception
                raise AgentNotFoundException(agent_id)

            get_data_response = invoked_agent.get_data()
            if not get_data_response:
                raise RuntimeError("Agent response data is empty")

            return get_data_response

        except AgentNotFoundException as e:
            self.logger.warning(f"Agent not found: {agent_id}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("invoking agent", e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while invoked the agent: {str(e)}")
            self.handle_unexpected_error("invoking agent", e)
            raise

    async def get_user_agents_with_statistics(self, user_id: int) -> dict:
        """Get user agents with statistics using use case."""
        try:
            from src.domain.use_cases.agent import GetUserAgentsInput

            result = await self.get_user_agents_use_case.execute(
                GetUserAgentsInput(user_id=user_id)
            )

            if result.is_error():
                raise Exception(result.get_error())

            if not result.data:
                raise Exception("No data returned from use case")

            self.log_context(
                f"Fetched {len(result.data.user_agents)} user agents for user_id={user_id}"
            )
            return {"user_agents": result.data.user_agents, "stats": result.data.stats}

        except Exception as e:
            self.handle_unexpected_error("getting user agents with statistics", e)
            raise


# Helper methods moved to use cases for better separation of concerns
