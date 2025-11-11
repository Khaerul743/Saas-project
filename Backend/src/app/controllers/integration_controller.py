from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.integration_schema import CreateIntegrationSchema
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.integration_exceptions import TelegramApiKeyNotFound
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.integration_service import IntegrationService


class IntegrationController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.integration_service = IntegrationService(db, request)

    async def create_integration(self, agent_id: str, payload: CreateIntegrationSchema):
        try:
            # Create new integration
            new_integration = await self.integration_service.create_integration(
                agent_id, payload
            )
            return new_integration

        except TelegramApiKeyNotFound as e:
            raise e
        except RuntimeError as e:
            raise e
        except UserNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
