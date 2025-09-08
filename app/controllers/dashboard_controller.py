import os
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Date, cast, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


def dashboard_overview(current_user: dict, db: Session):
    try:
        # --- Validasi user ---
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(
                f"User not found or not authenticated: user {current_user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # --- Query user + relasi agents ---
        user_with_agents = (
            db.query(User)
            .filter(User.id == current_user.get("id"))
            .options(
                joinedload(User.agents)
                .joinedload(Agent.user_agents)
                .joinedload(UserAgent.history_messages)
                .joinedload(HistoryMessage.message_metadata)
            )
            .first()
        )

        if not user_with_agents or not user_with_agents.agents:
            logger.info(f"No agents found for user {current_user.get('email')}")
            return {
                "token_usage": 0,
                "total_conversations": 0,
                "active_agents": 0,
                "average_response_time": 0,
                "success_rate": 0,
            }

        # --- Inisialisasi agregat ---
        total_tokens = 0
        total_conversations = 0
        active_agents = 0
        response_times = []
        success_count = 0

        for agent in user_with_agents.agents:
            if agent.status == "active":
                active_agents += 1

            for ua in agent.user_agents:
                for history in ua.history_messages:
                    total_conversations += 1
                    if history.message_metadata:
                        total_tokens += history.message_metadata.total_tokens or 0
                        if history.message_metadata.response_time:
                            response_times.append(
                                history.message_metadata.response_time
                            )
                        if history.message_metadata.is_success:
                            success_count += 1

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )
        success_rate = (
            (success_count / total_conversations) * 100
            if total_conversations > 0
            else 0
        )

        overview = {
            "token_usage": total_tokens,
            "total_conversations": total_conversations,
            "active_agents": active_agents,
            "average_response_time": round(avg_response_time, 2),
            "success_rate": round(success_rate, 2),
        }

        logger.info(
            f"Dashboard overview generated for user {current_user.get('email')}"
        )
        return overview
    except Exception as e:
        logger.error(
            f"Unexpected error while get conversation stats: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def token_usage_trend(
    current_user: dict,
    db: Session,
    start_date: datetime,
    end_date: datetime,
    group_by: str,
):
    """
    Returns token usage aggregated by period (day/week/month) for the current user's agents.

    Note: HistoryMessage does not have agent_id; we join:
      Metadata -> HistoryMessage -> UserAgent -> Agent -> User
    """
    try:
        # 1) validate user
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # 2) decide grouping expression (MySQL-friendly)
        # - day  -> DATE(created_at)
        # - week -> year-week (string) using %x-%v (ISO week/year)
        # - month-> YYYY-MM
        if group_by == "day":
            group_expr = func.date(HistoryMessage.created_at)
        elif group_by == "week":
            # returns like "21-35" (year-week) which is OK for grouping/ordering as string
            group_expr = func.date_format(HistoryMessage.created_at, "%x-%v")
        elif group_by == "month":
            group_expr = func.date_format(HistoryMessage.created_at, "%Y-%m")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid group_by value. Use day|week|month",
            )

        # 3) aggregate query:
        # Metadata -> HistoryMessage -> UserAgent -> Agent -> filter by Agent.user_id == user.id
        results = (
            db.query(
                group_expr.label("period"),
                func.coalesce(func.sum(Metadata.total_tokens), 0).label("total_tokens"),
            )
            .join(HistoryMessage, Metadata.history_message_id == HistoryMessage.id)
            .join(UserAgent, HistoryMessage.user_agent_id == UserAgent.id)
            .join(Agent, UserAgent.agent_id == Agent.id)
            .filter(Agent.user_id == user.id)
            .filter(
                HistoryMessage.created_at >= start_date,
                HistoryMessage.created_at <= end_date,
            )
            .group_by(group_expr)
            .order_by(group_expr.asc())
            .all()
        )

        # 4) normalize/format result
        trend = []
        for r in results:
            period = r.period
            # r.period might be a date object (for func.date) or string (for date_format)
            if hasattr(period, "isoformat"):  # date/datetime object
                period_str = period.isoformat()
            else:
                period_str = str(period)

            trend.append(
                {"period": period_str, "total_tokens": int(r.total_tokens or 0)}
            )

        return trend

    except HTTPException:
        # re-raise FastAPI HTTP errors unchanged
        raise
    except SQLAlchemyError as e:
        # DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while generating token usage trend.",
        )
    except Exception as e:
        # fallback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while generating token usage trend.",
        )


def get_conversation_trend(
    current_user: dict,
    db: Session,
    start_date: datetime,
    end_date: datetime,
    group_by: str,
):
    try:
        # validasi user
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(f"[Analytics] User not found: {current_user.get('id')}")
            raise ValueError("User not found or not authenticated")

        # tentukan grouping
        if group_by == "day":
            group_expr = cast(HistoryMessage.created_at, Date)
        elif group_by == "week":
            group_expr = func.date_trunc("week", HistoryMessage.created_at)
        elif group_by == "month":
            group_expr = func.date_trunc("month", HistoryMessage.created_at)
        else:
            logger.error(f"[Analytics] Invalid group_by value: {group_by}")
            raise ValueError("Invalid group_by value. Use 'day', 'week', or 'month'.")

        # query aggregate
        results = (
            db.query(
                group_expr.label("period"),
                func.count(HistoryMessage.id).label("total_conversations"),
            )
            .join(UserAgent, HistoryMessage.user_agent_id == UserAgent.id)
            .join(Agent, UserAgent.agent_id == Agent.id)
            .filter(Agent.user_id == user.id)
            .filter(
                HistoryMessage.created_at >= start_date,
                HistoryMessage.created_at <= end_date,
            )
            .group_by(group_expr)
            .order_by(group_expr.asc())
            .all()
        )

        # format hasil
        trend = [
            {
                "period": str(
                    r.period.date() if hasattr(r.period, "date") else r.period
                ),
                "total_conversations": int(r.total_conversations or 0),
            }
            for r in results
        ]

        logger.info(
            f"[Analytics] Conversation trend fetched for user={user.id}, group_by={group_by}, "
            f"from={start_date} to={end_date}, total_periods={len(trend)}"
        )

        return trend
    except HTTPException:
        # re-raise FastAPI HTTP errors unchanged
        raise
    except SQLAlchemyError as e:
        # DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while generating token usage trend.",
        )
    except Exception as e:
        logger.exception(f"[Analytics] Failed to get conversation trend: {e}")
        raise
