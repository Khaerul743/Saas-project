import os

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.history_model import HistoryOut
from app.models.history_message.metadata_entity import Metadata
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)



def get_all_messages_by_threadId(user_agent_id: str, current_user: dict, db: Session):
    try:
        agent = db.query(UserAgent).filter(UserAgent.id == user_agent_id).first()
        if not agent:
            logger.warning(
                f"User agent not found: User agent ID {user_agent_id} and user {current_user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User agent not found"
            )

        # Ambil semua history message + metadata
        conversations = (
            db.query(HistoryMessage)
            .options(joinedload(HistoryMessage.message_metadata))
            .filter(HistoryMessage.user_agent_id == user_agent_id)
            .order_by(HistoryMessage.created_at.asc())
            .all()
        )

        if not conversations:
            return {
                "history_message": [],
                "stats": {"token_usage": 0, "response_time": 0, "messages": 0},
            }

        # Format hasil untuk history_message
        history_data = [
            {
                "user_agent_id": conv.user_agent_id,
                "user_message": conv.user_message,
                "response": conv.response,
                "created_at": conv.created_at,
                "metadata": {
                    "total_tokens": conv.message_metadata.total_tokens
                    if conv.message_metadata
                    else None,
                    "response_time": conv.message_metadata.response_time
                    if conv.message_metadata
                    else None,
                    "model": conv.message_metadata.model
                    if conv.message_metadata
                    else None,
                    "is_success": conv.message_metadata.is_success
                    if conv.message_metadata
                    else None,
                },
            }
            for conv in conversations
        ]

        # Stats
        total_tokens = sum(
            conv.message_metadata.total_tokens
            for conv in conversations
            if conv.message_metadata
        )
        avg_response_time = (
            (
                sum(
                    conv.message_metadata.response_time
                    for conv in conversations
                    if conv.message_metadata
                )
                / len([c for c in conversations if c.message_metadata])
            )
            if any(conv.message_metadata for conv in conversations)
            else 0
        )
        total_messages = len(conversations)

        stats = {
            "token_usage": total_tokens,
            "response_time": round(avg_response_time, 2),
            "messages": total_messages,
        }

        return {"history_message": history_data, "stats": stats}

    except HTTPException:
        # biarin FastAPI yang handle
        raise
    except Exception as e:
        logger.error(f"Unexpected error while get all messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
