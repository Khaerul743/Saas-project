import os
from dataclasses import dataclass

from src.core.exceptions.document_store_exceptions import DirectoryPathNotFound
from src.domain.use_cases.agent.document.uploaded_document import UploadedDocumentOutput
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.vector_store.chroma_db import RAGSystem


@dataclass
class AddDocumentToAgentInput:
    agent_id: str
    document_detail: UploadedDocumentOutput


@dataclass
class AddDocumentToAgentOutput:
    collection_name: str


class AddDocumentToAgent(
    BaseUseCase[AddDocumentToAgentInput, AddDocumentToAgentOutput]
):
    def __init__(self, rag_system: RAGSystem):
        self.document_store = rag_system

    def execute(
        self, input_data: AddDocumentToAgentInput
    ) -> UseCaseResult[AddDocumentToAgentOutput]:
        try:
            document_detail = input_data.document_detail
            if not os.path.exists(document_detail.directory_path + "/"):
                raise DirectoryPathNotFound()

            # Initial collection name
            collection_name = f"agent_{input_data.agent_id}"
            self.document_store.initial_collection(collection_name)

            documents = self.document_store.load_single_document(
                document_detail.directory_path,
                document_detail.file_name,
                document_detail.content_type,
            )

            # Add document to vector store
            self.document_store.add_documents(
                documents, str(document_detail.document_id)
            )

            return UseCaseResult.success_result(
                AddDocumentToAgentOutput(collection_name)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while store document: {str(e)}", e
            )
