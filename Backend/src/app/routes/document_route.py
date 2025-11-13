from fastapi import (
    APIRouter,
    Depends,
    File,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.document_controller import DocumentController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.document_schema import (
    AddDocumentResponse,
    DeleteDocumentRequest,
    GetAllDocumentsResponse,
)
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.response import success_response

router = APIRouter(prefix="/api/documents", tags=["agents"])


@router.get(
    "/agent/{agent_id}",
    response_model=GetAllDocumentsResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def getAllDocuments(
    request: Request,
    agent_id: str,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = DocumentController(db, request)
    result = await controller.get_all_documents(agent_id)
    return success_response("Get all documents is successfully", result)


@router.post(
    "/agent/{agent_id}",
    response_model=AddDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def documentStore(
    request: Request,
    agent_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = DocumentController(db, request)
    result = await controller.add_document_to_agent(agent_id, file)
    return success_response("Add document to agent is successfully", result)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
)
async def deleteDocument(
    request: Request,
    document_id: str,
    agent_id: str,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = DocumentController(db, request)
    payload = DeleteDocumentRequest(agent_id=agent_id, document_id=document_id)
    result = await controller.delete_document(payload)
    return success_response(
        "Delete document is successfully", {"success": result.success}
    )
