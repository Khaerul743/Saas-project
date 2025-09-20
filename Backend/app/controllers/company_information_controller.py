from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.agent.agent_entity import Agent
from app.models.company_information.company_entity import CompanyInformation
from app.models.company_information.company_model import UpdateCompanyInformation
from app.utils.logger import get_logger
from app.utils.error_utils import (
    handle_database_error,
    handle_user_not_found,
)
from app.utils.validation_utils import (
    validate_user_exists,
    validate_agent_exists_and_owned,
)

logger = get_logger(__name__)


def get_all_company_information(db: Session, current_user: dict) -> List[dict]:
    """
    Get all company information for the authenticated user's agents.
    
    Args:
        db: Database session
        current_user: Current authenticated user data
        
    Returns:
        List[dict]: List of company information for user's agents
        
    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))
        
        # Query company information with agent relationship
        company_infos = (
            db.query(CompanyInformation)
            .join(Agent, CompanyInformation.agent_id == Agent.id)
            .filter(Agent.user_id == user.id)
            .options(
                joinedload(CompanyInformation.agent)
            )
            .all()
        )
        
        if not company_infos:
            logger.info(f"No company information found for user {current_user.get('email')}")
            return []  # Return empty list, not error
        
        # Format company information data
        company_info_list = []
        for company_info in company_infos:
            company_info_list.append({
                "id": company_info.id,
                "agent_id": company_info.agent_id,
                "agent_name": company_info.agent.name,
                "name": company_info.name,
                "industry": company_info.industry,
                "description": company_info.description,
                "address": company_info.address,
                "email": company_info.email,
                "website": company_info.website,
                "fallback_email": company_info.fallback_email,
                "created_at": company_info.created_at
            })
        
        logger.info(
            f"Successfully retrieved {len(company_info_list)} company information records for user {current_user.get('email')}"
        )
        return company_info_list
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise handle_database_error(e, "getting company information", current_user.get('email'))


def get_company_information_by_agent_id(db: Session, agent_id: int, current_user: dict) -> dict:
    """
    Get company information for a specific agent.
    
    Args:
        db: Database session
        agent_id: ID of the agent
        current_user: Current authenticated user data
        
    Returns:
        dict: Company information for the specified agent
        
    Raises:
        HTTPException: If agent not found, unauthorized, or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))
        
        # Get agent and verify ownership
        agent = validate_agent_exists_and_owned(db, agent_id, user.id, current_user.get('email'))
        
        # Query company information for the specific agent
        company_info = (
            db.query(CompanyInformation)
            .filter(CompanyInformation.agent_id == agent_id)
            .first()
        )
        
        if not company_info:
            logger.info(f"No company information found for agent {agent_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company information not found for this agent"
            )
        
        # Format company information data
        company_info_data = {
            "id": company_info.id,
            "agent_id": company_info.agent_id,
            "agent_name": agent.name,
            "name": company_info.name,
            "industry": company_info.industry,
            "description": company_info.description,
            "address": company_info.address,
            "email": company_info.email,
            "website": company_info.website,
            "fallback_email": company_info.fallback_email,
            "created_at": company_info.created_at
        }
        
        logger.info(
            f"Successfully retrieved company information for agent {agent_id} by user {current_user.get('email')}"
        )
        return company_info_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise handle_database_error(e, "getting company information by agent", current_user.get('email'))


def get_company_information_by_id(db: Session, company_info_id: int, current_user: dict) -> dict:
    """
    Get company information by its ID.
    
    Args:
        db: Database session
        company_info_id: ID of the company information
        current_user: Current authenticated user data
        
    Returns:
        dict: Company information data
        
    Raises:
        HTTPException: If company information not found, unauthorized, or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))
        
        # Query company information with agent relationship to verify ownership
        company_info = (
            db.query(CompanyInformation)
            .join(Agent, CompanyInformation.agent_id == Agent.id)
            .filter(
                CompanyInformation.id == company_info_id,
                Agent.user_id == user.id
            )
            .options(
                joinedload(CompanyInformation.agent)
            )
            .first()
        )
        
        if not company_info:
            logger.info(f"Company information {company_info_id} not found or not owned by user {current_user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company information not found"
            )
        
        # Format company information data
        company_info_data = {
            "id": company_info.id,
            "agent_id": company_info.agent_id,
            "agent_name": company_info.agent.name,
            "name": company_info.name,
            "industry": company_info.industry,
            "description": company_info.description,
            "address": company_info.address,
            "email": company_info.email,
            "website": company_info.website,
            "fallback_email": company_info.fallback_email,
            "created_at": company_info.created_at
        }
        
        logger.info(
            f"Successfully retrieved company information {company_info_id} by user {current_user.get('email')}"
        )
        return company_info_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise handle_database_error(e, "getting company information by ID", current_user.get('email'))


def update_company_information(
    db: Session, 
    company_info_id: int, 
    update_data: UpdateCompanyInformation, 
    current_user: dict
) -> dict:
    """
    Update company information by its ID.
    
    Args:
        db: Database session
        company_info_id: ID of the company information to update
        update_data: Update data for company information
        current_user: Current authenticated user data
        
    Returns:
        dict: Updated company information data
        
    Raises:
        HTTPException: If company information not found, unauthorized, or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))
        
        # Query company information with agent relationship to verify ownership
        company_info = (
            db.query(CompanyInformation)
            .join(Agent, CompanyInformation.agent_id == Agent.id)
            .filter(
                CompanyInformation.id == company_info_id,
                Agent.user_id == user.id
            )
            .options(
                joinedload(CompanyInformation.agent)
            )
            .first()
        )
        
        if not company_info:
            logger.info(f"Company information {company_info_id} not found or not owned by user {current_user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company information not found"
            )
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(company_info, field):
                setattr(company_info, field, value)
        
        # Commit changes to database
        db.commit()
        db.refresh(company_info)
        
        # Update agent object's company_information if agent exists in memory
        try:
            from app.controllers.document_controller import agents
            agent_id = str(company_info.agent_id)
            
            if agent_id in agents:
                # Create updated company information object for agent
                updated_company_info = {
                    "name": company_info.name,
                    "industry": company_info.industry,
                    "description": company_info.description,
                    "address": company_info.address,
                    "email": company_info.email,
                    "website": company_info.website,
                    "fallback_email": company_info.fallback_email,
                }
                
                # Update agent's company_information
                if hasattr(agents[agent_id], 'company_information'):
                    setattr(agents[agent_id], 'company_information', updated_company_info)
                    logger.info(f"Updated company_information in agent {agent_id} object")
                else:
                    # Try to set the attribute even if it doesn't exist
                    setattr(agents[agent_id], 'company_information', updated_company_info)
                    logger.info(f"Set company_information attribute in agent {agent_id} object")
            else:
                logger.info(f"Agent {agent_id} not found in memory, skipping agent object update")
                
        except Exception as agent_update_error:
            # Log error but don't fail the update
            logger.warning(f"Failed to update agent object company_information: {str(agent_update_error)}")
        
        # Format updated company information data
        updated_company_info_data = {
            "id": company_info.id,
            "agent_id": company_info.agent_id,
            "agent_name": company_info.agent.name,
            "name": company_info.name,
            "industry": company_info.industry,
            "description": company_info.description,
            "address": company_info.address,
            "email": company_info.email,
            "website": company_info.website,
            "fallback_email": company_info.fallback_email,
            "created_at": company_info.created_at
        }
        
        logger.info(
            f"Successfully updated company information {company_info_id} by user {current_user.get('email')}"
        )
        return updated_company_info_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "updating company information", current_user.get('email'))


def update_company_information_by_agent_id(
    db: Session, 
    agent_id: int, 
    update_data: UpdateCompanyInformation, 
    current_user: dict
) -> dict:
    """
    Update company information for a specific agent.
    
    Args:
        db: Database session
        agent_id: ID of the agent
        update_data: Update data for company information
        current_user: Current authenticated user data
        
    Returns:
        dict: Updated company information data
        
    Raises:
        HTTPException: If agent not found, unauthorized, or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))
        
        # Get agent and verify ownership
        agent = validate_agent_exists_and_owned(db, agent_id, user.id, current_user.get('email'))
        
        # Query company information for the specific agent
        company_info = (
            db.query(CompanyInformation)
            .filter(CompanyInformation.agent_id == agent_id)
            .first()
        )
        
        if not company_info:
            logger.info(f"No company information found for agent {agent_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company information not found for this agent"
            )
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(company_info, field):
                setattr(company_info, field, value)
        
        # Commit changes to database
        db.commit()
        db.refresh(company_info)
        
        # Update agent object's company_information if agent exists in memory
        try:
            from app.controllers.document_controller import agents
            agent_id_str = str(agent_id)
            
            if agent_id_str in agents:
                # Create updated company information object for agent
                updated_company_info = {
                    "name": company_info.name,
                    "industry": company_info.industry,
                    "description": company_info.description,
                    "address": company_info.address,
                    "email": company_info.email,
                    "website": company_info.website,
                    "fallback_email": company_info.fallback_email,
                }
                
                # Update agent's company_information
                if hasattr(agents[agent_id_str], 'company_information'):
                    setattr(agents[agent_id_str], 'company_information', updated_company_info)
                    logger.info(f"Updated company_information in agent {agent_id_str} object")
                else:
                    # Try to set the attribute even if it doesn't exist
                    setattr(agents[agent_id_str], 'company_information', updated_company_info)
                    logger.info(f"Set company_information attribute in agent {agent_id_str} object")
            else:
                logger.info(f"Agent {agent_id_str} not found in memory, skipping agent object update")
                
        except Exception as agent_update_error:
            # Log error but don't fail the update
            logger.warning(f"Failed to update agent object company_information: {str(agent_update_error)}")
        
        # Format updated company information data
        updated_company_info_data = {
            "id": company_info.id,
            "agent_id": company_info.agent_id,
            "agent_name": agent.name,
            "name": company_info.name,
            "industry": company_info.industry,
            "description": company_info.description,
            "address": company_info.address,
            "email": company_info.email,
            "website": company_info.website,
            "fallback_email": company_info.fallback_email,
            "created_at": company_info.created_at
        }
        
        logger.info(
            f"Successfully updated company information for agent {agent_id} by user {current_user.get('email')}"
        )
        print(f"agents: {agents[agent_id_str].company_information}")
        return updated_company_info_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "updating company information by agent", current_user.get('email'))
