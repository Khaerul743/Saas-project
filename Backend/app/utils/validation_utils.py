"""
Utility functions for data validation and user operations.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user.user_entity import User
from app.models.agent.agent_entity import Agent
from app.utils.error_utils import handle_user_not_found, handle_agent_not_found


def validate_user_exists(db: Session, user_id: int, user_email: Optional[str]) -> User:
    """
    Validate that user exists in database.
    
    Args:
        db: Database session
        user_id: User ID to validate
        user_email: User email for error logging
        
    Returns:
        User object if found
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise handle_user_not_found(user_email or "unknown")
    return user


def validate_agent_exists_and_owned(db: Session, agent_id: int, user_id: int, user_email: str) -> Agent:
    """
    Validate that agent exists and is owned by user.
    
    Args:
        db: Database session
        agent_id: Agent ID to validate
        user_id: User ID who should own the agent
        user_email: User email for error logging
        
    Returns:
        Agent object if found and owned by user
        
    Raises:
        HTTPException: If agent not found or not owned by user
    """
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == user_id
    ).first()
    
    if not agent:
        raise handle_agent_not_found(agent_id, user_email)
    
    return agent


def validate_agent_exists(db: Session, agent_id: int, user_email: str) -> Agent:
    """
    Validate that agent exists in database.
    
    Args:
        db: Database session
        agent_id: Agent ID to validate
        user_email: User email for error logging
        
    Returns:
        Agent object if found
        
    Raises:
        HTTPException: If agent not found
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise handle_agent_not_found(agent_id, user_email)
    return agent
