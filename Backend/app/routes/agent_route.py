import json
import os

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers.agent_controller import (
    delete_agent,
    get_all_user_agent,
    get_all_agents,
    update_agent,
)
from app.controllers.document_controller import document_store
from app.middlewares.RBAC import role_required
from app.models.agent.agent_model import CreateAgent, ResponseAPI, UpdateAgent
from app.utils.response import success_response

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def getAllAgent(
    request: Request,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        agents = get_all_agents(db, current_user)
        return success_response("Getting all agents is successfully", agents)
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


# Note: Create agent endpoint has been moved to specific agent type routes
# Use /api/agents/simple-rag for Simple RAG Agents
# Use /api/agents/customer-service for Customer Service Agents (to be implemented)


@router.put("/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def updateAgent(
    request: Request,
    agent_id: int,
    agent_data: UpdateAgent,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Update an existing agent for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the agent to update
        agent_data: Agent update data from request body
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with updated agent data
    """
    try:
        # Update agent using controller
        updated_agent = update_agent(db, agent_id, agent_data, current_user)

        # Return success response
        return success_response(
            message="Agent updated successfully", data=updated_agent
        )

    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def deleteAgent(
    request: Request,
    agent_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    try:
        response = delete_agent(agent_id, current_user, db)
        return success_response(response.get("message"))
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise

@router.get("/users", status_code=status.HTTP_200_OK)
def getAllUserAgent(
    current_user: dict = Depends(role_required(["user", "admin"])),
    db: Session = Depends(get_db),
):
    try:
        get_history = get_all_user_agent(current_user, db)
        return success_response("Get all history is successfully", get_history)
    except:
        raise