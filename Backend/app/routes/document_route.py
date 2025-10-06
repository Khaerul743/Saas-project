import os

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers import document_controller as dc
from app.middlewares.RBAC import role_required
from app.utils.response import success_response

router = APIRouter(prefix="/api/documents", tags=["agents"])


@router.get("/{agent_id}", status_code=status.HTTP_200_OK)
def getAllDocumentByAgentId(
    agent_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        documents = dc.get_documents_by_agent(agent_id, current_user, db)
        return success_response(
            "Get all document by agent id is successfully", documents
        )
    except Exception as e:
        raise


@router.post("", status_code=status.HTTP_201_CREATED)
async def documentStore(
    file: UploadFile = File(...),
    agent_id: str = Form(...),
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    try:
        print(file)
        print(agent_id)
        directory_path = "documents"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        response = await dc.document_store(
            file, agent_id, current_user, db, background_tasks
        )
        return success_response(
            "Store document is successfully",
            {"filename": response.file_name, "content_type": response.content_type},
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def deleteDocument(
    document_id: int,
    agent_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        response = dc.document_delete(document_id, agent_id, current_user, db)
        return success_response(response.get("detail"))
    except Exception as e:
        raise
