from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.agent.agent_entity import Agent
from app.models.agent.agent_model import (
    AgentOut,
    CreateAgent,
    GettingAllAgents,
    UpdateAgent,
)
from app.models.user.user_entity import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_all_agents(db: Session, current_user: dict):
    # Get user from database to ensure user exists
    try:
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(
                f"User not found for getting all agents: user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        agents = db.query(Agent).filter(Agent.user_id == current_user.get("id")).all()

        agents = [
            {
                "avatar": agent.avatar,
                "role": agent.role,
                "status": agent.status,
                "short_term_memory": agent.short_term_memory,
                "tone": agent.tone,
                "name": agent.name,
                "model": agent.model,
                "description": agent.description,
                "base_prompt": agent.base_prompt,
                "long_term_memory": agent.long_term_memory,
                "created_at": agent.created_at,
            }
            for agent in agents
        ]
        logger.info(f"{current_user.get('email')} successfully retrieved all agents")
        return agents
    except IntegrityError as e:
        logger.error(f"Database integrity error while getting agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Getting agents failed due to database constraint violation",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while getting all agents: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def create_agent(db: Session, agent_data: CreateAgent, current_user: dict) -> AgentOut:
    """
    Create a new agent for the authenticated user.

    Args:
        db: Database session
        agent_data: Agent creation data
        current_user: Current authenticated user data

    Returns:
        AgentOut: Created agent data

    Raises:
        HTTPException: If user not found or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(
                f"User not found for agent creation: user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Create new agent instance
        new_agent = Agent(
            user_id=user.id,
            name=agent_data.name,
            avatar=agent_data.avatar,
            model=agent_data.model,
            role=agent_data.role or "simple RAG agent",
            description=agent_data.description or "Tidak ada deskripsi",
            tone=agent_data.tone or "formal",
            short_term_memory=agent_data.short_term_memory or False,
            long_term_memory=agent_data.long_term_memory or False,
            status="active",
        )

        # Add to database
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)

        # Log successful creation
        logger.info(
            f"Agent '{new_agent.name}' created successfully by user {current_user.get('email')} "
            f"(user_id: {user.id}, agent_id: {new_agent.id})"
        )

        # Return agent data in expected format
        return AgentOut(
            name=new_agent.name,
            avatar=new_agent.avatar or "",
            model=new_agent.model,
            role=new_agent.role,
            description=new_agent.description or "",
            tone=new_agent.tone,
            status="active",
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error while creating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent creation failed due to database constraint violation",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def update_agent(
    db: Session, agent_id: int, agent_data: UpdateAgent, current_user: dict
) -> AgentOut:
    """
    Update an existing agent for the authenticated user.

    Args:
        db: Database session
        agent_id: ID of the agent to update
        agent_data: Agent update data
        current_user: Current authenticated user data

    Returns:
        AgentOut: Updated agent data

    Raises:
        HTTPException: If agent not found, unauthorized, or database error occurs
    """
    try:
        # Get user from database to ensure user exists
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(
                f"User not found for agent update: user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get agent and verify ownership
        agent = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.user_id == user.id)
            .first()
        )

        if not agent:
            logger.warning(
                f"Agent not found or unauthorized access: agent_id {agent_id}, "
                f"user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or you don't have permission to update this agent",
            )

        # Update agent fields (only update provided fields)
        update_data = agent_data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(agent, field):
                setattr(agent, field, value)

        # Commit changes
        db.commit()
        db.refresh(agent)

        # Log successful update
        logger.info(
            f"Agent '{agent.name}' (ID: {agent.id}) updated successfully by user "
            f"{current_user.get('email')} (user_id: {user.id})"
        )

        # Return updated agent data
        return AgentOut(
            name=agent.name,
            avatar=agent.avatar or "",
            model=agent.model,
            role=agent.role,
            description=agent.description or "",
            tone=agent.tone,
            status=agent.status,
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error while updating agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent update failed due to database constraint violation",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while updating agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def delete_agent(agent_id: int, current_user: dict, db: Session):
    try:
        user = db.query(User).filter(User.id == current_user.get("id")).first()
        if not user:
            logger.warning(
                f"User not found for agent delete: user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        agent = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.user_id == user.id)
            .first()
        )
        if not agent:
            logger.warning(
                f"Agent not found or unauthorized access: agent_id {agent_id}, "
                f"user_id {current_user.get('id')}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        db.delete(agent)
        db.commit()
        return {"message": f"delete agent is successfully: agent ID is {agent_id}"}
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error while deleting agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent delete failed due to database constraint violation",
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while deleting agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
