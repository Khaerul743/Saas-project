from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.document_entity import Document
from src.domain.use_cases.interfaces import DocumentRepositoryInterface


class DocumentRepository(DocumentRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_document_by_id(self, document_id: str):
        query = select(Document).where(Document.id == document_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_and_agent_id(self, document_id: str, agent_id: str):
        query = select(Document).where(
            Document.id == document_id, Document.agent_id == agent_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_document(self, agent_id: str, file_name: str, content_type: str):
        new_document = Document(
            agent_id=agent_id, file_name=file_name, content_type=content_type
        )
        self.db.add(new_document)
        await self.db.flush()
        await self.db.refresh(new_document)
        return new_document

    async def delete_document_by_id(self, document_id: str):
        document = await self.get_document_by_id(document_id)
        if not document:
            return None

        await self.db.delete(document)
        return document

    async def get_all_by_agent_id(self, agent_id: str) -> list[Document]:
        query = select(Document).where(Document.agent_id == agent_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
