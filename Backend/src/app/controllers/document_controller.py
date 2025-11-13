from datetime import datetime
from typing import Literal

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.document_schema import AddDocumentRequest, DeleteDocumentRequest
from src.core.exceptions.auth_exceptions import ValidationException
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.document_exceptions import (
    DocumentNotFound,
    FileTooLargeException,
)
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.document_service import DocumentService


class DocumentController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.document_service = DocumentService(db, request)

    async def get_all_documents(self, agent_id: str):
        try:
            result = await self.document_service.get_all_documents(agent_id)
            return result

        except RuntimeError as e:
            self.handle_unexpected_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def add_document_to_agent(self, agent_id: str, file: UploadFile):
        try:
            payload = AddDocumentRequest(agent_id=agent_id, file=file)
            result = await self.document_service.add_document_to_agent(payload)
            return result

        except ValueError:
            raise FileTooLargeException()

        except UserNotFoundException as e:
            raise e

        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def delete_document(self, payload: DeleteDocumentRequest):
        try:
            result = await self.document_service.delete_document(payload)
            return result

        except DocumentNotFound as e:
            raise e
        except RuntimeError as e:
            self.handle_unexpected_error(e)
            raise
        except Exception as e:
            self.handle_unexpected_error(e)
            raise
