from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.repositories import AgentRepository, UserRepository
from src.domain.service.base import BaseService
from src.domain.use_cases.dashboard import (
    GetDashboardOverview,
    GetDashboardOverviewInput,
)


class DashboardService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.user_repository = UserRepository(db)
        self.agent_repository = AgentRepository(db)
        self.get_dashboard_overview_uc = GetDashboardOverview(
            self.user_repository, self.agent_repository
        )

    async def get_dashboard_overview(self, user_id: int):
        """
        Get dashboard overview statistics for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary containing dashboard overview statistics

        Raises:
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            result = await self.get_dashboard_overview_uc.execute(
                GetDashboardOverviewInput(user_id=user_id)
            )

            if not result:
                self.logger.warning(
                    f"Failed to get dashboard overview: {result.get_error()} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserNotFoundException(user_id)

            data = result.get_data()
            if not data:
                raise RuntimeError("Dashboard overview data is empty")

            # Convert to dict format matching original response
            return {
                "token_usage": data.token_usage,
                "total_conversations": data.total_conversations,
                "active_agents": data.active_agents,
                "average_response_time": data.average_response_time,
                "success_rate": data.success_rate,
            }

        except UserNotFoundException as e:
            self.logger.warning(f"User not found: {user_id}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting dashboard overview", e)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting dashboard overview: {str(e)}"
            )
            self.handle_unexpected_error("getting dashboard overview", e)
            raise
