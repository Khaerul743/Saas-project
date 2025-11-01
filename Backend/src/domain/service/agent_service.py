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
from src.domain.service import BaseService
from src.domain.use_cases.agent import (
    CalculateAgentStatsUseCase,
    DeleteAgentUseCase,
    FormatAgentDataUseCase,
    GetAgentsWithDetailsUseCase,
    GetAllAgentsUseCase,
    GetUserAgentsUseCase,
)


class AgentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.agent_repo = AgentRepository(db)

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
