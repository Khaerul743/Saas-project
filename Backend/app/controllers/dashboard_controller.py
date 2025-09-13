import os
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_user_exists
from app.utils.calculate import (
    calculate_dashboard_overview,
    format_token_usage_trend_data,
    format_conversation_trend_data,
    format_total_tokens_per_agent_data,
    get_default_dashboard_response,
)

logger = get_logger(__name__)


def dashboard_overview(current_user: dict, db: Session):
    try:
        # --- Validasi user ---
        user = validate_user_exists(db, current_user.get("id"), current_user.get('email'))

        
        # return overview
        # --- Query user + relasi agents, tapi ambil kolom yang diperlukan saja ---
        user_with_agents = (
            db.query(User)
            .filter(User.id == current_user.get("id"))
            .options(
                joinedload(User.agents)
                .load_only(Agent.id, Agent.status)
                .joinedload(Agent.user_agents)
                .load_only(UserAgent.id)
                .joinedload(UserAgent.history_messages)
                .load_only(HistoryMessage.id)
                .joinedload(HistoryMessage.message_metadata)
                .load_only(
                    Metadata.total_tokens,
                    Metadata.response_time,
                    Metadata.is_success,
                )
            )
            .first()
        )

        if not user_with_agents or not user_with_agents.agents:
            logger.info(f"No agents found for user {current_user.get('email')}")
            return get_default_dashboard_response()

        # --- Calculate dashboard overview menggunakan utility function ---
        overview = calculate_dashboard_overview(user_with_agents.agents)

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
        user = validate_user_exists(db, current_user.get("id"), current_user.get('email'))

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

        # --- Format results menggunakan utility function ---
        trend = format_token_usage_trend_data(results)

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
        user = validate_user_exists(db, current_user.get("id"), current_user.get('email'))

        # tentukan grouping
        from sqlalchemy import Date, cast
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

        # --- Format results menggunakan utility function ---
        trend = format_conversation_trend_data(results)

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


def total_tokens_per_agent(current_user: dict, db: Session):
    """
    Ambil total tokens untuk setiap agent yang dimiliki user
    """
    try:
        user = validate_user_exists(db, current_user.get("id"), current_user.get('email'))
        
        # Aggregate total_tokens per agent
        results = (
            db.query(
                Agent.id.label("agent_id"),
                Agent.name.label("agent_name"),
                func.coalesce(func.sum(Metadata.total_tokens), 0).label("total_tokens"),
            )
            .join(UserAgent, UserAgent.agent_id == Agent.id)
            .join(HistoryMessage, HistoryMessage.user_agent_id == UserAgent.id)
            .join(Metadata, Metadata.history_message_id == HistoryMessage.id)
            .filter(Agent.user_id == user.id)
            .group_by(Agent.id, Agent.name)
            .order_by(Agent.id)
            .all()
        )
        
        # --- Format results menggunakan utility function ---
        agents_tokens = format_total_tokens_per_agent_data(results)

        return {"agents": agents_tokens}

    except HTTPException:
        # re-raise FastAPI HTTP errors unchanged
        raise
    except SQLAlchemyError as e:
        # DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while getting total token per agent.",
        )
    except Exception as e:
        logger.error(
            f"[Analytics] Failed to fetch total tokens per agent for user_id={current_user.get('id')}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch total tokens per agent"
        )
