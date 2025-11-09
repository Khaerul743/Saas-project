from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserAgentNotFoundException
from src.domain.service.history_service import HistoryService


class HistoryController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.history_service = HistoryService(db, request)

    async def get_all_messages_by_thread_id(self, user_agent_id: str):
        """
        Get all history messages for a user agent thread.

        Args:
            user_agent_id: ID of the user agent thread

        Returns:
            Dictionary containing history messages and statistics

        Raises:
            UserAgentNotFoundException: If user agent is not found
            DatabaseException: If database operation fails
        """
        try:
            result = await self.history_service.get_history_messages(user_agent_id)
            return result
        except UserAgentNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
