from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.dashboard_controller import DashboardController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.dashboard_schema import DashboardOverviewResponse
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.response import success_response

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def dashboard_overview(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard overview statistics for the current user.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with dashboard overview statistics
    """
    controller = DashboardController(db, request)
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    result = await controller.dashboard_overview(user_id)
    return success_response("Get agent conversation stats is successfully", result)
