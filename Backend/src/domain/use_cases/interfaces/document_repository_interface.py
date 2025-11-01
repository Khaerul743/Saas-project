from abc import ABC, abstractmethod

from src.domain.models.document_entity import Document


class DocumentRepositoryInterface(ABC):
    @abstractmethod
    async def add_document(
        self, agent_id: str, file_name: str, content_type: str
    ) -> Document:
        pass
