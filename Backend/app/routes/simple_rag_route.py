import json

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers.simple_rag_controller import (
    create_simple_rag_agent,
    delete_simple_rag_agent,
    update_simple_rag_agent,
)
from app.middlewares.RBAC import role_required
from app.models.agent.simple_rag_model import (
    CreateSimpleRAGAgent,
    SimpleRAGAgentResponse,
    UpdateSimpleRAGAgent,
)
from app.utils.response import success_response

router = APIRouter(prefix="/api/agents/simple-rag", tags=["simple-rag-agents"])


@router.post("", response_model=SimpleRAGAgentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def createSimpleRAGAgent(
    request: Request,
    file: UploadFile = None,
    agent_data: str = Form(...),
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Create a new Simple RAG Agent for the authenticated user.

    Args:
        request: FastAPI request object
        file: Optional uploaded file for document
        agent_data: Simple RAG Agent creation data from form
        current_user: Current authenticated user (from JWT token)
        db: Database session
        background_tasks: Optional background tasks

    Returns:
        SimpleRAGAgentResponse: Success response with created Simple RAG Agent data
    """
    try:
        # Parse agent data from form
        parsed_data = json.loads(agent_data)
        
        # Validate required fields for Simple RAG Agent
        if not parsed_data.get("base_prompt"):
            raise ValueError("base_prompt is required for Simple RAG Agent")
        if not parsed_data.get("tone"):
            raise ValueError("tone is required for Simple RAG Agent")
        
        # Set default role
        parsed_data["role"] = "simple RAG agent"
        
        created_agent = await create_simple_rag_agent(
            db,
            file,
            CreateSimpleRAGAgent(**parsed_data),
            current_user,
            background_tasks,
        )
        
        # Return success response
        return success_response(
            message="Simple RAG Agent created successfully", 
            data=created_agent
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.put("/{agent_id}", response_model=SimpleRAGAgentResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def updateSimpleRAGAgent(
    request: Request,
    agent_id: int,
    agent_data: UpdateSimpleRAGAgent,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Update an existing Simple RAG Agent for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the Simple RAG Agent to update
        agent_data: Simple RAG Agent update data from request body
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        SimpleRAGAgentResponse: Success response with updated Simple RAG Agent data
    """
    try:
        # Update Simple RAG Agent using controller
        updated_agent = update_simple_rag_agent(db, agent_id, agent_data, current_user)

        # Return success response
        return success_response(
            message="Simple RAG Agent updated successfully", 
            data=updated_agent
        )

    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def deleteSimpleRAGAgent(
    request: Request,
    agent_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Delete a Simple RAG Agent for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the Simple RAG Agent to delete
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        Success response message
    """
    try:
        response = delete_simple_rag_agent(agent_id, current_user, db)
        return success_response(response.get("message"))
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise
