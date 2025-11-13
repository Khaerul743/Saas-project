from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import DocumentRepositoryInterface


@dataclass
class GetAllDocumentsByAgentIdInput:
    agent_id: str


@dataclass
class DocumentItem:
    id: int
    agent_id: str
    file_name: str
    content_type: str
    created_at: str


@dataclass
class GetAllDocumentsByAgentIdOutput:
    documents: list[DocumentItem]


class GetAllDocumentsByAgentId(
    BaseUseCase[GetAllDocumentsByAgentIdInput, GetAllDocumentsByAgentIdOutput]
):
    def __init__(self, document_repository: DocumentRepositoryInterface):
        self.document_repository = document_repository

    async def execute(
        self, input_data: GetAllDocumentsByAgentIdInput
    ) -> UseCaseResult[GetAllDocumentsByAgentIdOutput]:
        try:
            documents = await self.document_repository.get_all_by_agent_id(
                input_data.agent_id
            )

            document_items = []
            for document in documents:
                # Format created_at safely
                created_at_str = ""
                if hasattr(document, "created_at") and document.created_at:  # type: ignore[attr-defined]
                    created_at_str = document.created_at.isoformat()  # type: ignore[attr-defined]

                document_items.append(
                    DocumentItem(
                        id=document.id,  # type: ignore[attr-defined]
                        agent_id=document.agent_id,  # type: ignore[attr-defined]
                        file_name=document.file_name,  # type: ignore[attr-defined]
                        content_type=document.content_type,  # type: ignore[assignment]
                        created_at=created_at_str,
                    )
                )

            return UseCaseResult.success_result(
                GetAllDocumentsByAgentIdOutput(documents=document_items)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting documents: {str(e)}", e
            )

