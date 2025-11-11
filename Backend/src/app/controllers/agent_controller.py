from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.base import BaseController
from src.app.validators.agent_schema import (
    BaseAgentSchema,
    InvokeAgentApiRequest,
    InvokeAgentRequest,
    InvokeAgentResponseData,
)
from src.core.exceptions.agent_exceptions import (
    AgentNotFoundException,
    InvalidApiKeyException,
)
from src.core.exceptions.database_exceptions import DatabaseException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.service.agent_service import AgentService


class AgentController(BaseController):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__()
        self.agent_service = AgentService(db, request)

    def _get_current_user_id(
        self,
        current_user_jwt: Optional[dict] = None,
        current_user_context: Optional[dict] = None,
    ):
        current_user_id = (
            current_user_context.get("id")
            if current_user_context
            else current_user_jwt.get("id")
            if current_user_jwt
            else None
        )
        if not current_user_id:
            raise UserNotFoundException(current_user_id)
        return int(current_user_id)

    async def get_all_agents(self, page: int, limit: int):
        try:
            data_agents = await self.agent_service.get_all_agents(
                page=page, limit=limit
            )
            return data_agents
        except Exception as e:
            self.handle_unexpected_error(e)

    async def get_all_agent_and_detail(self, current_user: dict):
        try:
            # Get user_id from current_user
            get_context_current_user = self.agent_service.current_user
            user_id = self._get_current_user_id(current_user, get_context_current_user)

            # Ensure user_id is an integer
            user_id = int(user_id)

            # Get agents with details using service
            agents_summary = (
                await self.agent_service.get_agents_with_details_by_user_id(user_id)
            )

            return agents_summary
        except UserNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)

    async def delete_agent(self, agent_id: str) -> BaseAgentSchema:
        try:
            agent = await self.agent_service.delete_agent(agent_id)
            return agent
        except AgentNotFoundException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def get_all_user_agent(self, current_user_jwt: dict):
        try:
            # Get current user from context
            current_user = self.agent_service.current_user
            user_id = self._get_current_user_id(current_user_jwt, current_user)
            # Get user agents with statistics using service
            result = await self.agent_service.get_user_agents_with_statistics(user_id)

            return result
        except Exception as e:
            self.handle_unexpected_error(e)

    async def invoke_agent_in_playground(
        self, agent_id: str, invoke_request: InvokeAgentRequest, current_user: dict
    ) -> InvokeAgentResponseData:
        """
        Invoke an agent with a user message.

        Args:
            agent_id: ID of the agent to invoke
            invoke_request: Request containing message, username, and platform
            current_user: Current authenticated user from JWT

        Returns:
            InvokeAgentResponseData with agent response and metadata

        Raises:
            AgentNotFoundException: If agent is not found
            UserNotFoundException: If user is not found
            DatabaseException: If database operation fails
        """
        try:
            # Get username from request or use email from current_user
            username = invoke_request.username

            # Invoke agent using service
            result = await self.agent_service.invoke_agent_in_playground(
                agent_id=agent_id,
                username=username,
                user_platform="api",
                user_message=invoke_request.message,
            )

            # Map result to response schema
            return InvokeAgentResponseData(
                user_message=result.user_message,
                response=result.response,
                total_tokens=result.total_tokens,
                response_time=result.response_time,
            )

        except AgentNotFoundException as e:
            raise e
        except UserNotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise

    async def invoke_agent_with_api_key(
        self, agent_id: str, api_key: str, payload: InvokeAgentApiRequest
    ):
        try:
            invoke_agent = await self.agent_service.invoke_agent_api(
                agent_id, api_key, payload
            )
            return InvokeAgentResponseData(
                user_message=payload.message,
                response=invoke_agent.response,
                total_tokens=invoke_agent.total_tokens,
                response_time=invoke_agent.response_time,
            )
        except InvalidApiKeyException as e:
            raise e
        except RuntimeError as e:
            raise e
        except Exception as e:
            self.handle_unexpected_error(e)
            raise


# Old function removed - logic moved to service layer


# logger = get_logger(__name__)


# Old function removed - logic moved to service layer


# def delete_agent(agent_id: int, current_user: dict, db: Session):
#     try:
#         user_id = current_user.get("id")
#         if not user_id:
#             raise handle_user_not_found(current_user.get("email", "unknown"))
#         user = validate_user_exists(db, user_id, current_user.get("email"))

#         agent = validate_agent_exists_and_owned(
#             db, agent_id, user.id, current_user.get("email")
#         )

#         # Remove agent from memory if it exists
#         try:
#             from app.controllers.document_controller import agents

#             agent_id_str = str(agent_id)
#             if agent_id_str in agents:
#                 del agents[agent_id_str]
#                 logger.info(f"Removed agent {agent_id_str} from memory")
#         except Exception as memory_error:
#             logger.warning(f"Failed to remove agent from memory: {str(memory_error)}")

#         # Delete agent (cascade will handle company_information, documents, etc.)
#         db.delete(agent)
#         db.commit()

#         logger.info(
#             f"Agent '{agent.name}' (ID: {agent_id}) deleted successfully by user {current_user.get('email')}"
#         )
#         return {"message": f"delete agent is successfully: agent ID is {agent_id}"}
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise

#     except Exception as e:
#         db.rollback()
#         raise handle_database_error(e, "deleting agent", current_user.get("email"))


# async def invoke_agent(
#     agent_id: str, agent_invoke: AgentInvoke, current_user: dict, db: Session
# ):
#     try:
#         user_id = current_user.get("id")
#         if not user_id:
#             raise handle_user_not_found(current_user.get("email", "unknown"))

#         get_agent = validate_agent_exists_and_owned(
#             db, agent_id, user_id, current_user.get("email")
#         )

#         agent = agents.get(agent_id, None)
#         check_agent_in_redis = await redis_storage.is_agent_exists(agent_id)
#         print(f"agent: {agent}")
#         if not agent and not check_agent_in_redis:
#             logger.warning(f"Agent not found")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Agent not found.",
#             )

#         elif check_agent_in_redis and not agent:
#             from app.utils.agent_utils import build_agent

#             await event_bus.publish(
#                 Event(
#                     event_type=EventType.AGENT_INVOKE,
#                     user_id=user_id,
#                     agent_id=agent_id,
#                     payload={"message": "Building the agent..."},
#                 )
#             )
#             agent = await build_agent(agent_id)
#             logger.info(f"Agent built from redis: {agent}")
#             if not agent:
#                 logger.warning(f"Agent not found")
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Agent not found.",
#                 )

#         get_user_agent = (
#             db.query(UserAgent).filter(UserAgent.agent_id == agent_id).first()
#         )
#         if not get_user_agent:
#             user_agent = UserAgent(
#                 id=str(agent_id),
#                 agent_id=agent_id,
#                 username="Testing by admin",
#                 user_platform="api",
#             )
#             db.add(user_agent)
#             db.flush()
#             user_agent_id = user_agent.id
#         else:
#             user_agent_id = get_user_agent.id
#         await event_bus.publish(
#             Event(
#                 event_type=EventType.AGENT_INVOKE,
#                 user_id=user_id,
#                 agent_id=agent_id,
#                 payload={"message": "Reasoning..."},
#             )
#         )
#         agent_response = agent.execute(
#             {"user_message": agent_invoke.message}, str(agent_id)
#         )
#         new_history_message = HistoryMessage(
#             user_agent_id=user_agent_id,
#             user_message=agent_invoke.message,
#             response=agent_response.get("response", ""),
#         )
#         db.add(new_history_message)
#         db.flush()
#         history_message_id = new_history_message.id
#         response_time = agent.response_time
#         token_usage = agent.token_usage
#         new_metadata = Metadata(
#             history_message_id=history_message_id,
#             total_tokens=token_usage,
#             response_time=response_time,
#             model=agent.llm_model,
#         )
#         db.add(new_metadata)
#         db.commit()
#         logger.info(
#             f"Agent '{get_agent.name}' (ID: {agent_id}) invoked successfully by user {current_user.get('email')}"
#         )
#         return {
#             "user_message": agent_invoke.message,
#             "response": agent_response.get("response", ""),
#         }
#     except HTTPException:
#         db.rollback()
#         raise
#     except Exception as e:
#         db.rollback()
#         raise handle_database_error(e, "invoking agent", current_user.get("email"))
