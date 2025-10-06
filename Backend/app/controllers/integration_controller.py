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
from app.models.platform.platform_entity import Platform
from app.services.telegram import set_webhook
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned
from app.utils.agent_utils import generate_api_key, validate_api_key
from app.services.telegram import delete_webhook
from app.models.integration.integration_model import UpdateIntegration
load_dotenv()
logger = get_logger(__name__)

def get_api_key_by_agent_id(agent_id: str, platform: str, db: Session) -> str:
    """
    Get api_key from integration platform using agent_id and platform type
    
    Args:
        agent_id: The agent ID
        platform: The platform type (telegram, api, etc.)
        db: Database session
        
    Returns:
        str: The api_key from the platform
        
    Raises:
        HTTPException: If integration not found
    """
    integration = (
        db.query(Integration)
        .join(Platform, Integration.id == Platform.integration_id)
        .filter(
            Integration.agent_id == agent_id,
            Integration.platform == platform
        )
        .options(joinedload(Integration.platform_config))
        .first()
    )
    
    if not integration:
        logger.warning(
            f"Integration not found: agent ID {agent_id} with platform {platform}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    
    return integration.platform_config.api_key

async def create_integration(
    agent_id: str, payload: CreateIntegration, current_user: dict, db: Session
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
            platform_integration = Platform(
                integration_id=integration_id, 
                platform_type="telegram",
                api_key=payload.api_key
            )
            db.add(platform_integration)
            db.flush()
            webhook = await set_webhook(payload.api_key, integration_id)
            if not webhook.get("status"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=webhook.get("response"),
                )
        
        if payload.platform == "api":
            api_key = generate_api_key(db, current_user.get("id"), agent_id)
            platform_integration = Platform(
                integration_id=new_integration.id, 
                platform_type="api",
                api_key=api_key
            )
            db.add(platform_integration)
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


def get_all_integrations(agent_id: str, current_user: dict, db: Session):
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

async def update_integration(agent_id: str, payload: UpdateIntegration, current_user: dict, db: Session):
    try:
        new_api_key = payload.api_key
        agent = validate_agent_exists_and_owned(db, agent_id, current_user.get("id"), current_user.get('email'))
        
        # Get the current api_key using helper function
        old_api_key = get_api_key_by_agent_id(agent_id, payload.platform, db)
        
        # Relational query to fetch integration with platform data using agent_id
        integration = (
            db.query(Integration)
            .join(Platform, Integration.id == Platform.integration_id)
            .filter(
                Integration.agent_id == agent_id,
                Integration.platform == payload.platform
            )
            .options(joinedload(Integration.platform_config))
            .first()
        )

        if payload.platform == "telegram":
            await delete_webhook(old_api_key)
            webhook_result = await set_webhook(new_api_key, integration.id)
            if not webhook_result.get("status"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=webhook_result.get("response"),
                )
        elif payload.platform == "api":
            # For API platform, just update the api_key
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform not supported",
            )
        
        # Update the api_key in platform
        integration.platform_config.api_key = new_api_key

        db.commit()
        db.refresh(integration)
        logger.info(
            f"Integration updated: agent ID {agent_id}, platform {payload.platform} and user {current_user.get('email')}"
        )
        return integration
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while updating integration: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )

async def delete_integration(
    agent_id: str, integration_id: int, current_user: dict, db: Session
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
        if integration.platform == "telegram":
            await delete_webhook(integration.platform_integration.api_key)
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
