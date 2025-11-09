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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# from app.controllers.simple_rag_controller import (
#     create_simple_rag_agent,
#     delete_simple_rag_agent,
#     update_simple_rag_agent,
# )
from app.models.agent.simple_rag_model import (
    CreateSimpleRAGAgent,
    SimpleRAGAgentAsyncResponse,
    SimpleRAGAgentResponse,
    UpdateSimpleRAGAgent,
)
from src.app.controllers.simple_rag_controller import SimpleRAGController
from src.app.middlewares.auth_middleware import role_based_access_control
from src.app.validators.agent_schema import CreateAgent, CreateAgentResponse
from src.config.database import get_db
from src.config.limiter import limiter
from src.core.utils.response import success_response

router = APIRouter(prefix="/api/agents/simple-rag", tags=["simple-rag-agents"])


# @router.post("/test/{agent_id}")
# async def test(
#     request: Request,
#     agent_id: str,
#     file: UploadFile,
#     current_user: dict = Depends(
#         role_based_access_control.role_required(["admin", "user"])
#     ),
#     db: AsyncSession = Depends(get_db),
# ):
#     controller = SimpleRAGController(db, request)
#     agent = await controller.create_agent()
#     return success_response("Document process is successfully", document)


@router.post(
    "", response_model=CreateAgentResponse, status_code=status.HTTP_202_ACCEPTED
)
@limiter.limit("10/minute")
async def createSimpleRAGAgent(
    request: Request,
    file: UploadFile = None,
    agent_data: str = Form(...),
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
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

        controller = SimpleRAGController(db, request)
        agent = await controller.create_agent(parsed_data, file)

        # Return async response directly (no need for success_response wrapper)
        return success_response("Created simpel rag agent is successfully", agent)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


# # @router.put(
# #     "/{agent_id}", response_model=SimpleRAGAgentResponse, status_code=status.HTTP_200_OK
# # )
# # @limiter.limit("10/minute")
# # async def updateSimpleRAGAgent(
# #     request: Request,
# #     agent_id: str,
# #     agent_data: UpdateSimpleRAGAgent,
# #     current_user: dict = Depends(role_required(["admin", "user"])),
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     Update an existing Simple RAG Agent for the authenticated user.

# #     Args:
# #         request: FastAPI request object
# #         agent_id: ID of the Simple RAG Agent to update
# #         agent_data: Simple RAG Agent update data from request body
# #         current_user: Current authenticated user (from JWT token)
# #         db: Database session

# #     Returns:
# #         SimpleRAGAgentResponse: Success response with updated Simple RAG Agent data
# #     """
# #     try:
# #         # Update Simple RAG Agent using controller
# #         updated_agent = await update_simple_rag_agent(
# #             db, agent_id, agent_data, current_user
# #         )

# #         # Return success response
# #         return success_response(
# #             message="Simple RAG Agent updated successfully", data=updated_agent
# #         )

# #     except Exception as e:
# #         # This will be handled by the global error handler middleware
# #         raise


# # @router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
# # @limiter.limit("10/minute")
# # def deleteSimpleRAGAgent(
# #     request: Request,
# #     agent_id: int,
# #     current_user: dict = Depends(role_required(["admin", "user"])),
# #     db: Session = Depends(get_db),
# # ):
# #     """
# #     Delete a Simple RAG Agent for the authenticated user.

# #     Args:
# #         request: FastAPI request object
# #         agent_id: ID of the Simple RAG Agent to delete
# #         current_user: Current authenticated user (from JWT token)
# #         db: Database session

# #     Returns:
# #         Success response message
# #     """
# #     try:
# #         response = delete_simple_rag_agent(agent_id, current_user, db)
# #         return success_response(response.get("message"))
# #     except Exception as e:
# #         # This will be handled by the global error handler middleware
# #         raise
