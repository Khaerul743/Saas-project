import json
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers import dashboard_controller as dc
from app.middlewares.RBAC import role_required
from app.utils.response import success_response

router = APIRouter(prefix="/api/dashboard", tags=["agents"])


@router.get("/overview", status_code=status.HTTP_200_OK)
def dashboard_overview(
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        conversation_stats = dc.dashboard_overview(current_user, db)
        return success_response(
            "Get agent conversation stats is successfully", conversation_stats
        )
    except:
        raise


@router.get("/analytics/tokens", status_code=status.HTTP_200_OK)
def token_usage_trend(
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
    start_date: datetime = Query(None, description="Tanggal mulai (YYYY-MM-DD)"),
    end_date: datetime = Query(None, description="Tanggal akhir (YYYY-MM-DD)"),
    group_by: str = Query(
        "day", regex="^(day|week|month)$", description="Group by interval"
    ),
):
    try:
        # Default: 7 hari terakhir kalau user gak kasih date
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        token_stats = dc.token_usage_trend(
            current_user=current_user,
            db=db,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )
        return success_response("Get token usage trend successfully", token_stats)
    except Exception as e:
        raise


@router.get("/analytics/conversations", status_code=status.HTTP_200_OK)
def conversation_trend(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day",
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        trend = dc.get_conversation_trend(
            current_user, db, start_date, end_date, group_by
        )
        return success_response("Get conversation trend successfully", trend)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception:
        raise


@router.get("/analytics/agents", status_code=status.HTTP_200_OK)
def tokenUsagePerAgent(
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        get_user_tokens = dc.total_tokens_per_agent(current_user, db)
        return success_response(
            "Get token usage per agent is successfully", get_user_tokens
        )
    except:
        raise
