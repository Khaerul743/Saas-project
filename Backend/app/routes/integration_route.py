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
from app.models.integration.integration_model import CreateIntegration
from app.utils.response import success_response

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/{agent_id}", status_code=status.HTTP_200_OK)
def getAllIntegrations(
    agent_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        integrations = ic.get_all_integrations(agent_id, current_user, db)
        return success_response(
            "Get all agent integrations is successfully", integrations
        )
    except:
        raise


@router.post("/{agent_id}", status_code=status.HTTP_201_CREATED)
async def createIntegration(
    agent_id: int,
    payload: CreateIntegration,
    current_user: dict = Depends(role_required(["user", "admin"])),
    db: Session = Depends(get_db),
):
    try:
        new_integration = await ic.create_integration(
            agent_id, payload, current_user, db
        )
        return success_response("Agent integration is successfully", new_integration)
    except Exception as e:
        raise


@router.delete("/{integration_id}", status_code=status.HTTP_200_OK)
def deleteIntegration(
    integration_id: int,
    agent_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        ic.delete_integration(agent_id, integration_id, current_user, db)
        return success_response("Delete integration is successfully")
    except:
        raise
