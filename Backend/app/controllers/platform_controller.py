from fastapi import HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.controllers.document_controller import agents
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.integration.integration_entity import Integration
from app.models.platform.platform_entity import Platform
from app.models.user_agent.user_agent_entity import UserAgent
from app.services.telegram import send_message
from app.core.logger import get_logger
from app.utils.message_utils import safe_message_length
from app.utils.agent_utils import validate_api_key
from app.utils.agent_utils import invoke_agent_logic

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
            db.query(Platform)
            .options(joinedload(Platform.integration))  # eager load Integration
            .filter(
                Platform.integration_id == telegram_id,
                Platform.platform_type == "telegram",
            )
            .first()
        )

        if not platform:
            logger.warning(f"Integration telegram not found: {telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_200_OK,
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

        api_key = platform.api_key
        if agent.status == "non-active":
            await send_message(
                str(api_key),
                chat_id,
                "Sorry, I'm not available right now. Please try again later.",
            )
            logger.warning(f"Agent is not active: {agent_id}")
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Agent is not active.",
            )
        generate_id = str(chat_id) + str(agent_id)

        agent_response = agent.execute(
            {"user_message": text, "total_token": 0}, generate_id
        )

        # Checking user agent
        user_agent = (
            db.query(UserAgent).filter(UserAgent.id == str(generate_id)).first()
        )
        if not user_agent:
            new_user_agent = UserAgent(
                id=generate_id,
                agent_id=agent_id,
                username=username,
                user_platform="telegram",
            )
            db.add(new_user_agent)
            db.flush()
            user_agent_id = new_user_agent.id
        else:
            user_agent_id = user_agent.id

        # Save history message with safe length handling
        new_history_message = HistoryMessage(
            user_agent_id=user_agent_id,
            user_message=safe_message_length(text),
            response=safe_message_length(agent_response.get("response", "")),
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

        response = await send_message(
            str(api_key),
            chat_id,
            safe_message_length(agent_response.get("response", ""), max_length=4096),
        )
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
            status_code=status.HTTP_200_OK,
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
            status_code=status.HTTP_200_OK,
            detail="Internal server error, please try again later.",
        )


async def api_handler(api_key: str, agent_id: str, data: dict, db: Session):
    username = data.get("username")
    unique_id = data.get("unique_id")
    user_message = data.get("user_message")
    try:
        if not validate_api_key(api_key, db, agent_id):
            logger.warning(f"Invalid API key: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid API key.",
            )

        # agent = agents.get(str(agent_id))
        # if not agent:
        #     logger.warning(f"Agent not found")
        #     raise HTTPException(
        #         status_code=status.HTTP_200_OK,
        #         detail="Agent not found.",
        #     )

        # if agent.status == "non-active":
        #     logger.warning(f"Agent is not active: {agent_id}")
        #     return {
        #         "username": username,
        #         "user_message": user_message,
        #         "response": "Sorry, I'm not active right now. Please try again later.",
        #     }

        generate_id = str(unique_id) + str(agent_id)
        response = await invoke_agent_logic(
            agent_id, str(user_message), db, generate_id
        )

        # agent_response = agent.execute(
        #     {"user_message": user_message, "total_token": 0}, generate_id
        # )

        user_agent = (
            db.query(UserAgent).filter(UserAgent.id == str(generate_id)).first()
        )
        if not user_agent:
            new_user_agent = UserAgent(
                id=generate_id,
                agent_id=agent_id,
                username=username,
                user_platform="api",
            )
            db.add(new_user_agent)
            db.flush()
            user_agent_id = new_user_agent.id
        else:
            user_agent_id = user_agent.id

        new_history_message = HistoryMessage(
            user_agent_id=user_agent_id,
            user_message=safe_message_length(str(user_message)),
            response=safe_message_length(response.get("response", "")),
        )
        db.add(new_history_message)
        db.flush()

        history_message_id = new_history_message.id
        response_time = response.get("response_time", 0)
        token_usage = response.get("token_usage", 0)

        new_metadata = Metadata(
            history_message_id=history_message_id,
            total_tokens=token_usage,
            response_time=response_time,
            model=response.get("model", "unknown"),
        )
        db.add(new_metadata)
        db.commit()

        return {
            "username": username,
            "user_message": user_message,
            "response": response.get("response", ""),
        }
    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error while sending api message: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Internal server error, please try again later.",
        )
