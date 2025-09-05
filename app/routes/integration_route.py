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
from app.controllers import integration_controller as ic
from app.middlewares.RBAC import role_required
from app.models.integration.integration_model import IntegrationBase
from app.utils.response import success_response

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post("/{agent_id}", status_code=status.HTTP_201_CREATED)
def createIntegration(
    agent_id: int,
    payload: IntegrationBase,
    current_user: dict = Depends(role_required(["user", "admin"])),
    db: Session = Depends(get_db),
):
    try:
        new_integration = ic.create_integration(agent_id, payload, current_user, db)
        return success_response("Agent integration is successfully", new_integration)
    except Exception as e:
        raise
