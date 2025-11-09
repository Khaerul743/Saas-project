from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserAgentNotFoundException
from src.domain.repositories.history_message_repository import HistoryMessageRepository
from src.domain.repositories.user_agent_repository import UserAgentRepository
from src.domain.service.base import BaseService
from src.domain.use_cases.agent.history_message import (
    GetHistoryMessagesByUserAgentId,
    GetHistoryMessagesInput,
)


class HistoryService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.history_message_repo = HistoryMessageRepository(db)
        self.user_agent_repo = UserAgentRepository(db)
        self.get_history_messages_uc = GetHistoryMessagesByUserAgentId(
            self.history_message_repo, self.user_agent_repo
        )

    async def get_history_messages(self, user_agent_id: str):
        """
        Get all history messages for a user agent with statistics.

        Args:
            user_agent_id: ID of the user agent thread

        Returns:
            Dictionary containing history messages and statistics

        Raises:
            UserAgentNotFoundException: If user agent is not found
            DatabaseException: If database operation fails
        """
        try:
            result = await self.get_history_messages_uc.execute(
                GetHistoryMessagesInput(user_agent_id=user_agent_id)
            )

            if not result:
                self.logger.warning(
                    f"Failed to get history messages: {result.get_error()} code={result.get_error_code()}"
                )
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise UserAgentNotFoundException(user_agent_id)

            data = result.get_data()
            if not data:
                raise RuntimeError("History messages data is empty")

            # Convert to dict format matching original response
            history_data = []
            for msg in data.history_message:
                history_data.append(
                    {
                        "user_agent_id": msg.user_agent_id,
                        "user_message": msg.user_message,
                        "response": msg.response,
                        "created_at": msg.created_at,
                        "metadata": msg.metadata,
                    }
                )

            return {
                "history_message": history_data,
                "stats": {
                    "token_usage": data.stats.token_usage,
                    "response_time": data.stats.response_time,
                    "messages": data.stats.messages,
                },
            }

        except UserAgentNotFoundException as e:
            self.logger.warning(f"User agent not found: {user_agent_id}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("getting history messages", e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while getting history messages: {str(e)}")
            self.handle_unexpected_error("getting history messages", e)
            raise
