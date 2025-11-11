from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.integration_schema import CreateIntegrationSchema
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.integration_exceptions import TelegramApiKeyNotFound
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.repositories import (
    ApiKeyRepository,
    IntegrationRepository,
    PlatformRepository,
)
from src.domain.service.base import BaseService
from src.domain.use_cases.agent import (
    ApiIntegration,
    ApiIntegrationInput,
    CreateIntegration,
    GenerateApiKey,
    TelegramIntegration,
    TelegramIntegrationInput,
)
from src.infrastructure.telegram import telegram_manager


class IntegrationService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.api_key_repository = ApiKeyRepository(db)
        self.integration_repository = IntegrationRepository(db)
        self.platform_repository = PlatformRepository(db)
        self.generate_api_key_usecase = GenerateApiKey(self.api_key_repository)
        self.create_integration_usecase = CreateIntegration(
            self.integration_repository, self.platform_repository
        )
        self.api_integration_usecase = ApiIntegration(
            self.generate_api_key_usecase, self.create_integration_usecase
        )
        self.telegram_integration_usecase = TelegramIntegration(
            self.create_integration_usecase, telegram_manager
        )

    async def create_integration(self, agent_id: str, payload: CreateIntegrationSchema):
        try:
            # Get user id from context
            user_id = self.current_user_id()
            print(f"payload: {payload}")
            if not user_id:
                raise UserNotFoundException("none")

            # Validate type integration
            if payload.platform == "api":
                # Create agent integration platform
                create_integration = await self.api_integration_usecase.execute(
                    ApiIntegrationInput(user_id, agent_id, payload.status)
                )

                if not create_integration.is_success():
                    get_exception = create_integration.get_exception()
                    if get_exception:
                        raise get_exception

            elif payload.platform == "telegram":
                if not payload.api_key:
                    raise TelegramApiKeyNotFound()

                # Create agent integration platform
                create_integration = await self.telegram_integration_usecase.execute(
                    TelegramIntegrationInput(agent_id, payload.api_key, payload.status)
                )

                if not create_integration.is_success():
                    get_exception = create_integration.get_exception()
                    if get_exception:
                        raise get_exception

            integration_data = create_integration.get_data()
            if integration_data is None:
                raise RuntimeError("Create integration is not returned data")

            await self.db.commit()
            return CreateIntegrationSchema(
                platform=payload.platform,
                status=payload.status,
                api_key=integration_data.api_key,
            )

        except TelegramApiKeyNotFound as e:
            self.logger.warning("Telegram api key not found")
            raise e
        except RuntimeError as e:
            self.logger.error(f"Run time error while create integration: {str(e)}")
            raise e

        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Create integration", e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while Create integration: {str(e)}")
            self.handle_unexpected_error("Create integration", e)
            raise
