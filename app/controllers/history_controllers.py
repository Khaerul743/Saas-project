import os

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.history_model import HistoryOut
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_all_user_agent(agent_id: int, current_user: dict, db: Session):
    try:
        agent = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.user_id == current_user.get("id"))
            .first()
        )
        if not agent:
            logger.warning(
                f"Agent not found: Agent ID {agent_id} and user {current_user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )
        user_agents = db.query(UserAgent).filter(UserAgent.agent_id == agent_id).all()
        all_user_agents = [
            {
                "agent_id": data.agent_id,
                "username": data.username,
                "user_platform": data.user_platform,
            }
            for data in user_agents
        ]
        logger.info(
            f"Get all user agent is successfully: Agent ID {agent_id} and user {current_user.get('email')}"
        )

        return all_user_agents
    except HTTPException:
        # biarin FastAPI yang handle
        raise
    except Exception as e:
        logger.error(f"Unexpected error while get all messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def get_all_messages_by_threadId(user_agent_id: int, current_user: dict, db: Session):
    try:
        agent = db.query(UserAgent).filter(UserAgent.id == user_agent_id).first()
        if not agent:
            logger.warning(
                f"User agent not found: User agent ID {user_agent_id} and user {current_user.get('email')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User agent not found"
            )

        conversations = (
            db.query(HistoryMessage)
            .filter(
                HistoryMessage.user_agent_id == user_agent_id,
            )
            .all()
        )

        conversations = [
            HistoryOut(
                user_agent_id=conversation.user_agent_id,
                user_message=conversation.user_message,
                response=conversation.response,
                created_at=conversation.created_at,
            )
            for conversation in conversations
        ]
        logger.info(
            f"Get all messages by thread id is successfully: User agent ID {user_agent_id} and user {current_user.get('email')}"
        )
        return conversations
    except HTTPException:
        # biarin FastAPI yang handle
        raise
    except Exception as e:
        logger.error(f"Unexpected error while get all messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
