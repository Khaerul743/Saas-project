from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.integration_controller import IntegrationController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.integration_schema import (
    CreateIntegrationResponse,
    CreateIntegrationSchema,
)
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.response import success_response

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post(
    "/{agent_id}",
    response_model=CreateIntegrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def createIntegration(
    request: Request,
    agent_id: str,
    payload: CreateIntegrationSchema,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = IntegrationController(db, request)
    create_integration = await controller.create_integration(agent_id, payload)
    return success_response(
        "Create agent integration is successfully", create_integration
    )
