from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.integration_schema import CreateIntegrationSchema
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.integration_exceptions import (
    IntegrationIsAlreadyExist,
    IntegrationNotFoundException,
    PlatformDoesntSupportException,
    TelegramApiKeyNotFound,
)
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.integration_service import IntegrationService


class IntegrationController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.integration_service = IntegrationService(db, request)

    async def get_all_integrations(self, agent_id: str):
        try:
            result = await self.integration_service.get_all_integrations(agent_id)
            return result

        except RuntimeError as e:
            self.handle_unexpected_error(e)
            raise
        except DatabaseException as e:
            self.handle_unexpected_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def create_integration(self, agent_id: str, payload: CreateIntegrationSchema):
        try:
            # Create new integration
            new_integration = await self.integration_service.create_integration(
                agent_id, payload
            )
            return new_integration
        except IntegrationIsAlreadyExist as e:
            raise e
        except PlatformDoesntSupportException as e:
            raise e
        except TelegramApiKeyNotFound as e:
            raise e
        except RuntimeError as e:
            self.handle_unexpected_error(e)
            raise
        except UserNotFoundException as e:
            self.handle_unexpected_error(e)
            raise
        except DatabaseException as e:
            self.handle_unexpected_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def delete_integration(self, agent_id: str, platform: str):
        try:
            result = await self.integration_service.delete_integration(
                agent_id, platform
            )
            return result

        except PlatformDoesntSupportException as e:
            raise e
        except IntegrationNotFoundException as e:
            raise e
        except TelegramApiKeyNotFound as e:
            raise e
        except RuntimeError as e:
            self.handle_unexpected_error(e)
            raise
        except DatabaseException as e:
            self.handle_unexpected_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
