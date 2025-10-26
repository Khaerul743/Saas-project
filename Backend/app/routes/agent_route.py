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
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers.agent_controller import AgentController
from app.middlewares.auth_middleware import role_based_access_control
from app.schema.agent_schema import (
    AgentDeleteResponse,
    AgentDetailResponse,
    AgentPaginateResponse,
    UserAgentResponse,
)
from app.utils.response import success_response

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=AgentPaginateResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def getAllAgent(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=100),
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = AgentController(db, request)
    agents = await controller.get_all_agents(page, limit)
    return success_response("Getting all agents paginate is successfully", agents)


@router.get(
    "/details", response_model=AgentDetailResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("10/minute")
async def getAllAgentWithDetails(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = AgentController(db, request)
    agents = await controller.get_all_agent_and_detail(current_user)
    return success_response("Getting all agents with details is successfully", agents)


@router.delete(
    "/{agent_id}", response_model=AgentDeleteResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("10/minute")
async def deleteAgent(
    request: Request,
    agent_id: str,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = AgentController(db, request)
    agent = await controller.delete_agent(agent_id)
    return success_response("Delete agent has successfully", agent)


@router.get("/users", response_model=UserAgentResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def getAllUserAgent(
    request: Request,
    current_user: dict = Depends(
        role_based_access_control.role_required(["admin", "user"])
    ),
    db: AsyncSession = Depends(get_db),
):
    controller = AgentController(db, request)
    result = await controller.get_all_user_agent(current_user)
    return success_response("Get all user agents is successfully", result)


# Note: Create agent endpoint has been moved to specific agent type routes
# Use /api/agents/simple-rag for Simple RAG Agents
# Use /api/agents/customer-service for Customer Service Agents (to be implemented)


# @router.put("/{agent_id}", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
# def updateAgent(
#     request: Request,
#     agent_id: int,
#     agent_data: UpdateAgent,
#     current_user: dict = Depends(role_required(["admin", "user"])),
#     db: Session = Depends(get_db),
# ):
#     """
#     Update an existing agent for the authenticated user.

#     Args:
#         request: FastAPI request object
#         agent_id: ID of the agent to update
#         agent_data: Agent update data from request body
#         current_user: Current authenticated user (from JWT token)
#         db: Database session

#     Returns:
#         ResponseAPI: Success response with updated agent data
#     """
#     try:
#         # Update agent using controller
#         updated_agent = update_agent(db, agent_id, agent_data, current_user)

#         # Return success response
#         return success_response(
#             message="Agent updated successfully", data=updated_agent
#         )

#     except Exception as e:
#         # This will be handled by the global error handler middleware
#         raise

# @router.post("/invoke/{agent_id}")
# async def invokeAgent(
#     agent_id: str,
#     agent_invoke: AgentInvoke,
#     current_user: dict = Depends(role_required(["admin", "user"])),
#     db: Session = Depends(get_db),
# ):
#     try:
#         response = await invoke_agent(agent_id, agent_invoke, current_user, db)
#         return success_response("Invoke agent is successfully", response)
#     except:
#         raise
