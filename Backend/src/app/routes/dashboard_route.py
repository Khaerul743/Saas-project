from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.dashboard_controller import DashboardController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.dashboard_schema import (
    ConversationTrendResponse,
    DashboardOverviewResponse,
    TotalTokensPerAgentResponse,
    TokenUsageTrendResponse,
)
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
    result = await controller.dashboard_overview()
    return success_response("Get agent conversation stats is successfully", result)


@router.get(
    "/analytics/tokens",
    response_model=TokenUsageTrendResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def token_usage_trend(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
    start_date: datetime | None = Query(
        None, description="Tanggal mulai (YYYY-MM-DD)"
    ),
    end_date: datetime | None = Query(None, description="Tanggal akhir (YYYY-MM-DD)"),
    group_by: str = Query(
        "day", regex="^(day|week|month)$", description="Group by interval"
    ),
):
    """
    Get token usage trend aggregated by period for the current user's agents.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (from JWT token)
        db: Database session
        start_date: Start date for the trend (default: 7 days ago)
        end_date: End date for the trend (default: now)
        group_by: Grouping period (day, week, or month)

    Returns:
        ResponseAPI: Success response with token usage trend data
    """
    # Default: 7 hari terakhir kalau user gak kasih date
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()

    controller = DashboardController(db, request)
    result = await controller.token_usage_trend(
        start_date, end_date, group_by  # type: ignore[arg-type]
    )
    return success_response("Get token usage trend successfully", {"trend": result})


@router.get(
    "/analytics/conversations",
    response_model=ConversationTrendResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def conversation_trend(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
    start_date: datetime | None = Query(
        None, description="Tanggal mulai (YYYY-MM-DD)"
    ),
    end_date: datetime | None = Query(None, description="Tanggal akhir (YYYY-MM-DD)"),
    group_by: str = Query(
        "day", regex="^(day|week|month)$", description="Group by interval"
    ),
):
    """
    Get conversation trend aggregated by period for the current user's agents.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (from JWT token)
        db: Database session
        start_date: Start date for the trend (default: 7 days ago)
        end_date: End date for the trend (default: now)
        group_by: Grouping period (day, week, or month)

    Returns:
        ResponseAPI: Success response with conversation trend data
    """
    # Default: 7 hari terakhir kalau user gak kasih date
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()

    controller = DashboardController(db, request)
    result = await controller.conversation_trend(
        start_date, end_date, group_by  # type: ignore[arg-type]
    )
    return success_response("Get conversation trend successfully", {"trend": result})


@router.get(
    "/analytics/agents",
    response_model=TotalTokensPerAgentResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("30/minute")
async def total_tokens_per_agent(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get total tokens aggregated per agent for the current user's agents.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with total tokens per agent data
    """
    controller = DashboardController(db, request)
    result = await controller.total_tokens_per_agent()
    return success_response("Get total tokens per agent successfully", result)