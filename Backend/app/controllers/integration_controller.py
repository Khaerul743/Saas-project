# auth_controller.py
import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.integration.integration_entity import Integration
from app.models.integration.integration_model import CreateIntegration, IntegrationOut
from app.models.platform.telegram_entity import Telegram
from app.services.telegram import set_webhook
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned
from app.utils.agent_utils import generate_api_key, validate_api_key
from app.models.platform.api_entity import Api
load_dotenv()
logger = get_logger(__name__)

async def create_integration(
    agent_id: int, payload: CreateIntegration, current_user: dict, db: Session
):
    try:
        agent = validate_agent_exists_and_owned(db, agent_id, current_user.get("id"), current_user.get('email'))
        # agent = db.query(Agent).filter(
        #     Agent.id == agent_id, Agent.user_id == current_user.get("id")
        # )
        # if not agent:
        #     logger.warning(
        #         f"Agent not found: ID {agent_id} and user ID {current_user.get('id')}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        #     )

        new_integration = Integration(
            agent_id=agent_id, platform=payload.platform, status=payload.status
        )

        db.add(new_integration)
        db.flush()

        if payload.platform == "telegram":
            integration_id = new_integration.id
            telegram_integration = Telegram(
                integration_id=integration_id, api_key=payload.api_key
            )
            db.add(telegram_integration)
            db.flush()
            webhook = await set_webhook(payload.api_key, integration_id)
            if not webhook.get("status"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=webhook.get("response"),
                )
        
        if payload.platform == "api":
            api_key = generate_api_key(db, current_user.get("id"), agent_id)
            api_integration = Api(
                integration_id=new_integration.id, api_key=api_key
            )
            db.add(api_integration)
            db.flush()

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


def get_all_integrations(agent_id: int, current_user: dict, db: Session):
    try:
        # agent = (
        #     db.query(Agent)
        #     .filter(Agent.id == agent_id, Agent.user_id == current_user.get("id"))
        #     .first()
        # )
        # if not agent:
        #     logger.warning(
        #         f"Agent not found: agent ID {agent_id} and user {current_user.get('email')}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        #     )
        agent = validate_agent_exists_and_owned(db, agent_id, current_user.get("id"), current_user.get('email'))
        # Use joinedload to prevent n+1 problem if you need related objects

        integrations = (
            db.query(Integration)
            .filter(Integration.agent_id == agent_id)
            .options(joinedload(Integration.agent))  # adjust if you need related data
            .all()
        )

        result = [
            IntegrationOut(
                agent_id=integration.agent_id,
                platform=integration.platform,
                status=integration.status,
                created_at=integration.created_at,
            )
            for integration in integrations
        ]

        logger.info(
            f"Successfully fetched all integrations: Agent ID {agent_id} and user {current_user.get('email')}"
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while fetching integrations: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def delete_integration(
    agent_id: int, integration_id: int, current_user: dict, db: Session
):
    try:
        agent = validate_agent_exists_and_owned(db, agent_id, current_user.get("id"), current_user.get('email'))
        # agent = (
        #     db.query(Agent)
        #     .filter(Agent.id == agent_id, Agent.user_id == current_user.get("id"))
        #     .first()
        # )
        # if not agent:
        #     logger.warning(
        #         f"Agent not found: agent ID {agent_id} and user {current_user.get('email')}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        #     )
        integration = (
            db.query(Integration)
            .filter(Integration.id == integration_id, Integration.agent_id == agent_id)
            .first()
        )
        if not integration:
            logger.warning(
                f"Integration not found: integration ID {integration_id} for agent ID {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found",
            )
        db.delete(integration)
        db.commit()
        logger.info(
            f"Integration deleted: integration ID {integration_id} for agent ID {agent_id} and user {current_user.get('email')}"
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while deleting integration: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
