from fastapi import UploadFile
from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class AddDocumentRequest(BaseModel):
    agent_id: str
    file: UploadFile


class AddDocumentResponseData(BaseModel):
    agent_id: str
    filename: str
    content_type: str


class AddDocumentResponse(BaseSchemaOut):
    data: AddDocumentResponseData


class DocumentItemSchema(BaseModel):
    id: int
    agent_id: str
    file_name: str
    content_type: str
    created_at: str


class GetAllDocumentsData(BaseModel):
    documents: list[DocumentItemSchema]


class GetAllDocumentsResponse(BaseSchemaOut):
    data: GetAllDocumentsData


class DeleteDocumentRequest(BaseModel):
    agent_id: str
    document_id: str
