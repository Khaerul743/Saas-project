from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.telegram_schema import TelegramSendMessage
from src.core.exceptions.integration_exceptions import (
    TelegramApiKeyNotFound,
    TelegramResponseException,
)
from src.domain.repositories import (
    AgentRepository,
    ApiKeyRepository,
    HistoryMessageRepository,
    MetadataRepository,
    UserAgentRepository,
)
from src.domain.service.base import BaseService
from src.domain.use_cases.agent import (
    CreateHistoryMessage,
    CreateMetadata,
    CreateUserAgent,
    InitialAgentAgain,
    InitialSimpleRagAgent,
    InvokeAgent,
    InvokeAgentInput,
    SendTelegramUserMessage,
    SendTelegramUserMessageInput,
    StoreAgentInMemory,
)
from src.infrastructure.ai.agents import BaseAgentStateModel
from src.infrastructure.data import agent_manager
from src.infrastructure.redis.redis_storage import RedisStorage
from src.infrastructure.telegram import telegram_manager


class WebhookService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.user_agent_repo = UserAgentRepository(db)
        self.history_message_repo = HistoryMessageRepository(db)
        self.metadata_repo = MetadataRepository(db)
        self.api_key_repo = ApiKeyRepository(db)
        self.storage_agent_obj = RedisStorage()

        self.create_user_agent = CreateUserAgent(self.user_agent_repo)
        self.store_agent_in_memory = StoreAgentInMemory(agent_manager)
        self.initial_simple_rag_agent = InitialSimpleRagAgent(
            self.store_agent_in_memory
        )
        self.create_user_agent = CreateUserAgent(self.user_agent_repo)
        self.create_history_message = CreateHistoryMessage(self.history_message_repo)
        self.create_metadata = CreateMetadata(self.metadata_repo)

        self.initial_agent_again = InitialAgentAgain(self.initial_simple_rag_agent)
        self.invoke_agent_use_case = InvokeAgent(
            self.agent_repo,
            self.user_agent_repo,
            self.create_user_agent,
            self.create_history_message,
            self.create_metadata,
            agent_manager,
            self.storage_agent_obj,
            self.initial_agent_again,
        )

        self.send_telegram_user_message_usecase = SendTelegramUserMessage(
            self.api_key_repo, telegram_manager
        )

    async def invoked_agent_and_send_to_telegram(self, payload: TelegramSendMessage):
        try:
            invoked_agent = await self.invoke_agent_use_case.execute(
                InvokeAgentInput(
                    payload.agent_id,
                    str(payload.chat_id),
                    payload.username,
                    "telegram",
                    BaseAgentStateModel(messages=[], user_message=payload.text),
                )
            )

            if not invoked_agent.is_success():
                get_error = invoked_agent.error_code
                self.logger.error(f"Error while invoked the agent: {get_error}")
                raise TelegramResponseException()

            response = invoked_agent.get_data()
            if response is None:
                self.logger.error(
                    f"Invoked agent is not returned the response: {response}"
                )
                raise TelegramResponseException()

            sending_message = await self.send_telegram_user_message_usecase.execute(
                SendTelegramUserMessageInput(
                    payload.agent_id, payload.chat_id, response.response
                )
            )

            if not sending_message.is_success():
                get_error = sending_message.get_error()
                self.logger.error(f"Error while sending telegram message: {get_error}")
                raise TelegramResponseException()

            await self.db.commit()
        except TelegramResponseException as e:
            self.logger.error("Server error, but sending success to telegram webhook")
            raise e
        except TelegramApiKeyNotFound as e:
            self.logger.error(
                f"Error sending telegram message, because telegram api key not found: {str(e)}"
            )
            raise TelegramResponseException()
        except Exception as e:
            self.logger.error(
                f"Unexpexted error while invoked agent and sending to telegram: {str(e)}"
            )
            raise TelegramResponseException()
