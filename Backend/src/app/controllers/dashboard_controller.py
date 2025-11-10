from datetime import datetime
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.core.exceptions.auth_exceptions import ValidationException
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.dashboard_service import DashboardService


class DashboardController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.dashboard_service = DashboardService(db, request)

    async def dashboard_overview(self):
        """
        Get dashboard overview statistics for the current user.

        Returns:
            Dictionary containing dashboard overview statistics

        Raises:
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            result = await self.dashboard_service.get_dashboard_overview()
            return result
        except UserNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def token_usage_trend(
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
            result = await self.dashboard_service.get_token_usage_trend(
                start_date, end_date, group_by
            )
            return result
        except UserNotFoundException as e:
            raise e
        except ValidationException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def conversation_trend(
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
            result = await self.dashboard_service.get_conversation_trend(
                start_date, end_date, group_by
            )
            return result
        except UserNotFoundException as e:
            raise e
        except ValidationException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def total_tokens_per_agent(self):
        """
        Get total tokens aggregated per agent for the current user's agents.

        Returns:
            Dictionary containing list of agents with their total tokens

        Raises:
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            result = await self.dashboard_service.get_total_tokens_per_agent()
            return result
        except UserNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
