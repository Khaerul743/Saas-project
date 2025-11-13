from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.integration_schema import CreateIntegrationSchema
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.integration_exceptions import (
    IntegrationIsAlreadyExist,
    IntegrationNotFoundException,
    PlatformDoesntSupportException,
    TelegramApiKeyNotFound,
)
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
    DeleteApiIntegration,
    DeleteApiIntegrationInput,
    DeleteTelegramIntegration,
    DeleteTelegramIntegrationInput,
    GenerateApiKey,
    GetAllIntegrationByAgentId,
    GetAllIntegrationByAgentIdInput,
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
        self.delete_telegram_integration_usecase = DeleteTelegramIntegration(
            self.api_key_repository, self.integration_repository, telegram_manager
        )
        self.delete_api_integration_usecase = DeleteApiIntegration(
            self.integration_repository, self.api_key_repository
        )
        self.get_all_integration_by_agent_id_usecase = GetAllIntegrationByAgentId(
            self.integration_repository
        )

    async def get_all_integrations(self, agent_id: str) -> dict:
        try:
            result = await self.get_all_integration_by_agent_id_usecase.execute(
                GetAllIntegrationByAgentIdInput(agent_id=agent_id)
            )

            if not result.is_success():
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise RuntimeError("Get all integrations failed without exception")

            data = result.get_data()
            if data is None:
                raise RuntimeError("Get all integrations did not return data")

            # Convert IntegrationItem dataclass to dict for response
            integrations_list = []
            for integration_item in data.integrations:
                integrations_list.append(
                    {
                        "id": integration_item.id,
                        "agent_id": integration_item.agent_id,
                        "platform": integration_item.platform,
                        "status": integration_item.status,
                        "api_key": integration_item.api_key,
                        "created_at": integration_item.created_at,
                    }
                )

            return {"integrations": integrations_list}

        except RuntimeError as e:
            self.logger.error(f"Runtime error while getting integrations: {str(e)}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Get all integrations", e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while getting integrations: {str(e)}")
            self.handle_unexpected_error("Get all integrations", e)
            raise

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

            else:
                raise PlatformDoesntSupportException()

            integration_data = create_integration.get_data()
            if integration_data is None:
                raise RuntimeError("Create integration is not returned data")

            await self.db.commit()
            return CreateIntegrationSchema(
                platform=payload.platform,
                status=payload.status,
                api_key=integration_data.api_key,
            )
        except IntegrationIsAlreadyExist as e:
            raise e
        except PlatformDoesntSupportException as e:
            raise e
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

    async def delete_integration(self, agent_id: str, platform: str) -> dict[str, bool]:
        try:
            if platform == "telegram":
                delete_result = await self.delete_telegram_integration_usecase.execute(
                    DeleteTelegramIntegrationInput(
                        agent_id=agent_id, platform="telegram"
                    )
                )
            elif platform == "api":
                delete_result = await self.delete_api_integration_usecase.execute(
                    DeleteApiIntegrationInput(agent_id=agent_id, platform="api")
                )
            else:
                raise PlatformDoesntSupportException()

            if not delete_result.is_success():
                get_exception = delete_result.get_exception()
                if get_exception:
                    raise get_exception
                raise RuntimeError("Delete integration failed without exception")

            data = delete_result.get_data()
            if data is None:
                raise RuntimeError("Delete integration did not return data")

            await self.db.commit()

            return {"success": data.success}

        except PlatformDoesntSupportException as e:
            raise e
        except IntegrationNotFoundException as e:
            self.logger.warning(f"Integration not found with agent {agent_id}")
            raise e
        except TelegramApiKeyNotFound as e:
            self.logger.warning("Telegram api key not found while deleting webhook")
            raise e
        except RuntimeError as e:
            self.logger.error(f"Runtime error while deleting integration: {str(e)}")
            raise e
        except DatabaseException as e:
            self.handle_database_error(e)
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error("Delete integration", e)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while deleting integration: {str(e)}")
            self.handle_unexpected_error("Delete integration", e)
            raise
