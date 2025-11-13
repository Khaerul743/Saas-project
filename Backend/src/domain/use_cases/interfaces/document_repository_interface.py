from abc import ABC, abstractmethod

from src.domain.models.document_entity import Document


class DocumentRepositoryInterface(ABC):
    @abstractmethod
    async def add_document(
        self, agent_id: str, file_name: str, content_type: str
    ) -> Document:
        pass

    @abstractmethod
    async def get_by_id_and_agent_id(
        self, document_id: str, agent_id: str
    ) -> Document | None:
        pass

    @abstractmethod
    async def get_document_by_id(self, document_id: str) -> Document | None:
        pass

    @abstractmethod
    async def delete_document_by_id(self, document_id: str) -> Document | None:
        pass

    @abstractmethod
    async def get_all_by_agent_id(self, agent_id: str) -> list[Document]:
        pass
