"""
Utility functions for consistent error handling across controllers.
"""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logger import get_logger

logger = get_logger(__name__)


def handle_database_error(error: Exception, operation: str, user_email: Optional[str] = None) -> HTTPException:
    """
    Handle database errors consistently across controllers.
    
    Args:
        error: The database error that occurred
        operation: Description of the operation that failed
        user_email: Optional user email for logging
        
    Returns:
        HTTPException with appropriate error details
    """
    if isinstance(error, SQLAlchemyError):
        logger.error(f"Database error during {operation}: {str(error)}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later.",
        )
    else:
        logger.error(f"Unexpected error during {operation}: {str(error)}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later.",
        )


def handle_user_not_found(user_email: str) -> HTTPException:
    """
    Handle user not found errors consistently.
    
    Args:
        user_email: Email of the user that was not found
        
    Returns:
        HTTPException for user not found
    """
    logger.warning(f"User not found or not authenticated: user {user_email}")
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )


def handle_agent_not_found(agent_id: int, user_email: str) -> HTTPException:
    """
    Handle agent not found errors consistently.
    
    Args:
        agent_id: ID of the agent that was not found
        user_email: Email of the user making the request
        
    Returns:
        HTTPException for agent not found
    """
    logger.warning(f"Agent not found: agent_id {agent_id} for user {user_email}")
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Agent not found or you don't have permission to access this agent",
    )


def handle_validation_error(field: str, value: str) -> HTTPException:
    """
    Handle validation errors consistently.
    
    Args:
        field: Name of the field that failed validation
        value: Value that failed validation
        
    Returns:
        HTTPException for validation error
    """
    logger.warning(f"Validation error for field '{field}': {value}")
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid value for field '{field}': {value}",
    )
