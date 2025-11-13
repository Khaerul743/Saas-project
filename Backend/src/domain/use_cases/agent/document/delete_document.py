from dataclasses import dataclass

from src.core.exceptions.document_exceptions import DocumentNotFound
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import DocumentRepositoryInterface
from src.infrastructure.vector_store.chroma_db import RAGSystem


@dataclass
class DeleteDocumentInput:
    agent_id: str
    document_id: str


@dataclass
class DeleteDocumentOutput:
    success: bool


class DeleteDocument(BaseUseCase[DeleteDocumentInput, DeleteDocumentOutput]):
    def __init__(
        self, document_repository: DocumentRepositoryInterface, rag_system: RAGSystem
    ):
        self.document_repository = document_repository
        self.document_store = rag_system

    async def execute(
        self, input_data: DeleteDocumentInput
    ) -> UseCaseResult[DeleteDocumentOutput]:
        try:
            # Make sure document is exist
            document = await self.document_repository.get_by_id_and_agent_id(
                input_data.document_id, input_data.agent_id
            )

            if not document:
                return UseCaseResult.error_result(
                    "Document not found", DocumentNotFound(input_data.document_id)
                )

            # Initital collection name
            collection_name = f"agent_{input_data.agent_id}"
            self.document_store.initial_collection(collection_name)

            # Delete document in database
            delete_document = await self.document_repository.delete_document_by_id(
                input_data.document_id
            )
            if not delete_document:
                return UseCaseResult.error_result(
                    "Document not found", DocumentNotFound(input_data.document_id)
                )

            # Delete document in vectore store
            self.document_store.delete_document(input_data.document_id)

            return UseCaseResult.success_result(DeleteDocumentOutput(True))

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while deleting document: {str(e)}", e
            )
