import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.controllers.document_controller import agents
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.integration.integration_entity import Integration
from app.models.platform.telegram_entity import Telegram
from app.models.user_agent.user_agent_entity import UserAgent
from app.services.telegram import send_message
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def telegram_handler(data: dict, db: Session):
    telegram_id = data.get("telegram_id")
    chat_id = data.get("chat_id")
    text = data.get("text")
    username = data.get("username")

    if not telegram_id or not chat_id or not text:
        logger.warning(f"Chat detail not found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: telegram_id, chat_id, or text.",
        )

    try:
        platform = (
            db.query(Telegram)
            .options(joinedload(Telegram.integration))  # eager load Integration
            .filter(Telegram.integration_id == telegram_id)
            .first()
        )

        if not platform:
            logger.warning(f"Integration telegram not found: {telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration or Telegram not found.",
            )

        # langsung ambil integration dari relationship
        integration = platform.integration
        agent_id = integration.agent_id
        # # Use joinedload to eagerly load related integration and agent in one query
        # platform = (
        #     db.query(Telegram).filter(Telegram.integration_id == telegram_id).first()
        # )
        # if not platform:
        #     logger.warning(f"Integration telegram not found: {telegram_id}")
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Integration or Telegram not found.",
        #     )

        # integration = (
        #     db.query(Integration)
        #     .filter(Integration.id == platform.integration_id)
        #     .first()
        # )
        # agent_id = integration.agent_id
        agent = agents.get(str(agent_id))
        if not agent:
            logger.warning(f"Agent not found")
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Agent not found.",
            )

        agent_response = agent.execute(
            {"user_message": text, "total_token": 0}, chat_id
        )
        api_key = platform.api_key

        # Checking user agent
        user_agent = db.query(UserAgent).filter(UserAgent.id == str(chat_id)).first()
        print(user_agent)
        if not user_agent:
            new_user_agent = UserAgent(
                id=chat_id,
                agent_id=agent_id,
                username=username,
                user_platform="telegram",
            )
            db.add(new_user_agent)
            db.flush()
            user_agent_id = new_user_agent.id
        else:
            user_agent_id = user_agent.id

        # Save history message
        new_history_message = HistoryMessage(
            user_agent_id=user_agent_id,
            user_message=text,
            response=agent_response.get("response"),
        )
        db.add(new_history_message)
        db.flush()

        history_message_id = new_history_message.id
        response_time = agent.response_time
        token_usage = agent.token_usage

        new_metadata = Metadata(
            history_message_id=history_message_id,
            total_tokens=token_usage,
            response_time=response_time,
            model=agent.llm_model,
        )

        db.add(new_metadata)

        response = await send_message(api_key, chat_id, agent_response.get("response"))
        if not response.get("status"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.get("response"),
            )
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError sending telegram message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later.",
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while sending telegram message: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later.",
        )
