from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.document_schema import (
    AddDocumentRequest,
    AddDocumentResponseData,
    DeleteDocumentRequest,
)
from src.core.exceptions.document_exceptions import DocumentNotFound
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.core.utils.save_file import SaveFileHandler
from src.domain.repositories import DocumentRepository
from src.domain.service.base import BaseService
from src.domain.use_cases.agent import (
    AddDocumentToAgent,
    AddDocumentToAgentInput,
    DeleteDocument,
    DeleteDocumentInput,
    GetAllDocumentsByAgentId,
    GetAllDocumentsByAgentIdInput,
    UploadedDocumentHandler,
    UploadedDocumentInput,
)
from src.infrastructure.vector_store.chroma_db import RAGSystem


class DocumentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.save_file = SaveFileHandler()

        self.vector_store = RAGSystem("chroma_db")

        # Use Cases
        self.uploaded_document_handler_usecase = UploadedDocumentHandler(
            self.document_repo, self.save_file
        )
        self.add_document_to_agent_usecase = AddDocumentToAgent(self.vector_store)
        self.delete_document_usecase = DeleteDocument(
            self.document_repo, self.vector_store
        )
        self.get_all_documents_by_agent_id_usecase = GetAllDocumentsByAgentId(
            self.document_repo
        )

    async def get_all_documents(self, agent_id: str) -> dict:
        try:
            result = await self.get_all_documents_by_agent_id_usecase.execute(
                GetAllDocumentsByAgentIdInput(agent_id=agent_id)
            )

            if not result.is_success():
                get_exception = result.get_exception()
                if get_exception:
                    raise get_exception
                raise RuntimeError("Get all documents failed without exception")

            data = result.get_data()
            if data is None:
                raise RuntimeError("Get all documents did not return data")

            # Convert DocumentItem dataclass to dict for response
            documents_list = []
            for document_item in data.documents:
                documents_list.append(
                    {
                        "id": document_item.id,
                        "agent_id": document_item.agent_id,
                        "file_name": document_item.file_name,
                        "content_type": document_item.content_type,
                        "created_at": document_item.created_at,
                    }
                )

            return {"documents": documents_list}

        except RuntimeError as e:
            self.logger.error(f"Runtime error while getting documents: {str(e)}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error while getting documents: {str(e)}")
            self.handle_unexpected_error("Get all documents", e)
            raise

    async def add_document_to_agent(
        self, payload: AddDocumentRequest
    ) -> AddDocumentResponseData:
        try:
            user_id = self.current_user_id()
            if not user_id:
                raise UserNotFoundException("none")
            save_document = await self.uploaded_document_handler_usecase.execute(
                UploadedDocumentInput(user_id, payload.agent_id, payload.file)
            )

            if not save_document.is_success():
                exception = save_document.get_exception()
                if exception:
                    raise exception

            document_data = save_document.get_data()
            if not document_data:
                raise RuntimeError("Uploaded document use case does not returned data")

            add_to_agent = self.add_document_to_agent_usecase.execute(
                AddDocumentToAgentInput(payload.agent_id, document_data)
            )

            if not add_to_agent.is_success():
                exception = add_to_agent.get_exception()
                if exception:
                    raise exception

            result_data = add_to_agent.get_data()
            if not result_data:
                raise RuntimeError(
                    "Add document to agent use case does not returned data"
                )
            await self.db.commit()
            return AddDocumentResponseData(
                agent_id=payload.agent_id,
                filename=document_data.file_name,
                content_type=document_data.content_type,
            )

        except ValueError as e:
            self.logger.warning(e)
            raise e

        except UserNotFoundException as e:
            raise e

        except RuntimeError as e:
            self.logger.error(f"Runtime error: {str(e)}")
            raise e

        except Exception as e:
            self.logger.error(f"Unexpected error while add document to agent: {str(e)}")
            raise e

    async def delete_document(self, payload: DeleteDocumentRequest):
        try:
            delete_docs = await self.delete_document_usecase.execute(
                DeleteDocumentInput(payload.agent_id, payload.document_id)
            )
            if not delete_docs.is_success():
                exception = delete_docs.get_exception()
                if exception:
                    raise exception

            result = delete_docs.get_data()
            if not result:
                raise RuntimeError("Delete document use case does not returned data")

            await self.db.commit()
            return result
        except DocumentNotFound as e:
            self.logger.warning(e)
            raise e

        except RuntimeError as e:
            self.logger.error(f"Runtime error: {e}")
            raise e

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e
