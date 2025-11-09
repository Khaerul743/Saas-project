from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.dashboard_service import DashboardService


class DashboardController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.dashboard_service = DashboardService(db, request)

    async def dashboard_overview(self, user_id: int):
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
            result = await self.dashboard_service.get_dashboard_overview(user_id)
            return result
        except UserNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
