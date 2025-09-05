# auth_controller.py
from fastapi import HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.agent.agent_entity import Agent
from app.models.integration.integration_entity import Integration
from app.models.integration.integration_model import IntegrationBase, IntegrationOut
from app.models.platform.telegram_entity import Telegram
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_integration(
    agent_id: int, payload: IntegrationBase, current_user: dict, db: Session
):
    try:
        agent = db.query(Agent).filter(
            Agent.id == agent_id, Agent.user_id == current_user.get("id")
        )
        if not agent:
            logger.warning(
                f"Agent not found: ID {agent_id} and user ID {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )

        new_integration = Integration(
            agent_id=agent_id, platform=payload.platform, status=payload.status
        )

        db.add(new_integration)
        db.flush()

        if payload.platform == "telegram":
            integration_id = new_integration.id
            telegram_integration = Telegram(
                integration_id=integration_id, api_key="init"
            )
            db.add(telegram_integration)

        db.commit()
        db.refresh(new_integration)
        logger.info(
            f"Agent integration to platform {new_integration.platform} is successfuly: agent ID {agent_id} and user ID {current_user.get('id')}"
        )
        return IntegrationOut(
            agent_id=agent_id,
            platform=new_integration.platform,
            status=new_integration.status,
            created_at=new_integration.created_at,
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError while add document: {str(e)}")
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
            f"Unexpected error while store the document: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
