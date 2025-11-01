from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.document_entity import Document
from src.domain.use_cases.interfaces import DocumentRepositoryInterface


class DocumentRepository(DocumentRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(self, agent_id: str, file_name: str, content_type: str):
        new_document = Document(
            agent_id=agent_id, file_name=file_name, content_type=content_type
        )
        self.db.add(new_document)
        await self.db.flush()
        await self.db.refresh(new_document)
        return new_document
