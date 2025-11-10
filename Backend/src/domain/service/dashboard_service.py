from datetime import datetime
from typing import Literal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.auth_exceptions import ValidationException
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.repositories import (
    AgentRepository,
    HistoryMessageRepository,
    MetadataRepository,
    UserRepository,
)
from src.domain.service.base import BaseService
from src.domain.use_cases.dashboard import (
    GetConversationTrend,
    GetConversationTrendInput,
    GetDashboardOverview,
    GetDashboardOverviewInput,
    GetTokenUsageTrend,
    GetTokenUsageTrendInput,
    GetTotalTokensPerAgent,
    GetTotalTokensPerAgentInput,
)


class DashboardService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.user_repository = UserRepository(db)
        self.agent_repository = AgentRepository(db)
        self.metadata_repository = MetadataRepository(db)
        self.history_message_repository = HistoryMessageRepository(db)
        self.get_dashboard_overview_uc = GetDashboardOverview(
            self.user_repository, self.agent_repository
        )
        self.get_token_usage_trend_uc = GetTokenUsageTrend(
            self.user_repository, self.metadata_repository
        )
        self.get_conversation_trend_uc = GetConversationTrend(
            self.user_repository, self.history_message_repository
        )
        self.get_total_tokens_per_agent_uc = GetTotalTokensPerAgent(
            self.user_repository, self.agent_repository
        )

    async def get_dashboard_overview(self):
        """
        Get dashboard overview statistics for the current user.

        Returns:
            Dictionary containing dashboard overview statistics

        Raises:
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            user_id = self.current_user_id()
            if not user_id:
                raise UserNotFoundException("none")

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
            self.logger.warning("User not found in context")
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

    async def get_token_usage_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ):
        """
        Get token usage trend aggregated by period for the current user's agents.

        Args:
            start_date: Start date for the trend
            end_date: End date for the trend
            group_by: Grouping period (day, week, or month)

        Returns:
            List of dictionaries containing period and total_tokens

        Raises:
            UserNotFoundException: If user is not found
            ValidationException: If group_by is invalid or date range is invalid
            DatabaseException: If database operation fails
        """
        try:
            user_id = self.current_user_id()
            if not user_id:
                raise UserNotFoundException("none")

            result = await self.get_token_usage_trend_uc.execute(
                GetTokenUsageTrendInput(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    group_by=group_by,
                )
            )

            if not result:
                self.logger.warning(
                    f"Failed to get token usage trend: {result.get_error()} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise ValidationException("token_usage_trend", result.get_error() or "Unknown error")

            data = result.get_data()
            if not data:
                raise RuntimeError("Token usage trend data is empty")

            # Convert to list format matching original response
            trend = [
                {"period": item.period, "total_tokens": item.total_tokens}
                for item in data.trend
            ]

            return trend

        except UserNotFoundException as e:
            self.logger.warning("User not found in context")
            raise e
        except ValidationException as e:
            self.logger.warning(f"Validation error: {str(e)}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting token usage trend", e)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting token usage trend: {str(e)}"
            )
            self.handle_unexpected_error("getting token usage trend", e)
            raise

    async def get_conversation_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: Literal["day", "week", "month"],
    ):
        """
        Get conversation trend aggregated by period for the current user's agents.

        Args:
            start_date: Start date for the trend
            end_date: End date for the trend
            group_by: Grouping period (day, week, or month)

        Returns:
            List of dictionaries containing period and total_conversations

        Raises:
            UserNotFoundException: If user is not found
            ValidationException: If group_by is invalid or date range is invalid
            DatabaseException: If database operation fails
        """
        try:
            user_id = self.current_user_id()
            if not user_id:
                raise UserNotFoundException("none")

            result = await self.get_conversation_trend_uc.execute(
                GetConversationTrendInput(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    group_by=group_by,
                )
            )

            if not result:
                self.logger.warning(
                    f"Failed to get conversation trend: {result.get_error()} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise ValidationException(
                    "conversation_trend", result.get_error() or "Unknown error"
                )

            data = result.get_data()
            if not data:
                raise RuntimeError("Conversation trend data is empty")

            # Convert to list format matching original response
            trend = [
                {"period": item.period, "total_conversations": item.total_conversations}
                for item in data.trend
            ]

            return trend

        except UserNotFoundException as e:
            self.logger.warning("User not found in context")
            raise e
        except ValidationException as e:
            self.logger.warning(f"Validation error: {str(e)}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting conversation trend", e)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting conversation trend: {str(e)}"
            )
            self.handle_unexpected_error("getting conversation trend", e)
            raise

    async def get_total_tokens_per_agent(self):
        """
        Get total tokens aggregated per agent for the current user's agents.

        Returns:
            Dictionary containing list of agents with their total tokens

        Raises:
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            user_id = self.current_user_id()
            if not user_id:
                raise UserNotFoundException("none")

            result = await self.get_total_tokens_per_agent_uc.execute(
                GetTotalTokensPerAgentInput(user_id=user_id)
            )

            if not result:
                self.logger.warning(
                    f"Failed to get total tokens per agent: {result.get_error()} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserNotFoundException(user_id)

            data = result.get_data()
            if not data:
                raise RuntimeError("Total tokens per agent data is empty")

            # Convert to list format matching original response
            agents = [
                {
                    "agent_id": item.agent_id,
                    "agent_name": item.agent_name,
                    "total_tokens": item.total_tokens,
                }
                for item in data.agents
            ]

            return {"agents": agents}

        except UserNotFoundException as e:
            self.logger.warning("User not found in context")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting total tokens per agent", e)
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error while getting total tokens per agent: {str(e)}"
            )
            self.handle_unexpected_error("getting total tokens per agent", e)
            raise
