from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.response import success_response
from src.app.controllers.history_controller import HistoryController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.history_schema import HistoryResponse
from src.config.database import get_db
from src.config.limiter import limiter

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get(
    "/messages/{user_agent_id}",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def getAllMessageByThreadId(
    request: Request,
    user_agent_id: str,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all history messages for a user agent thread.

    Args:
        request: FastAPI request object
        user_agent_id: ID of the user agent thread
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with history messages and statistics
    """
    controller = HistoryController(db, request)
    result = await controller.get_all_messages_by_thread_id(user_agent_id)
    return success_response("Get all history messages is successfully", result)
