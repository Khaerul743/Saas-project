import os
import shutil
from typing import List

from fastapi import BackgroundTasks, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.query import Query

from app.AI import simple_RAG_agent as AI
from app.controllers.document_controller import agents
from app.dependencies.redis_storage import redis_storage
from app.events.redis_event import Event, EventType, event_bus

# from app.controllers.document_controller import agents
from app.models.agent.agent_entity import Agent
from app.models.agent.agent_model import (
    AgentInvoke,
    AgentOut,
    CreateAgent,
    GettingAllAgents,
    UpdateAgent,
)
from app.models.company_information.company_entity import CompanyInformation
from app.models.document.document_entity import Document
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.integration.integration_entity import Integration
from app.models.platform.platform_entity import Platform
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.agent_utils import (
    calculate_agent_statistics,
    format_user_agents_data,
    get_default_stats_response,
)
from app.utils.document_utils import write_document
from app.utils.error_utils import (
    handle_agent_not_found,
    handle_database_error,
    handle_user_not_found,
)
from app.core.logger import get_logger
from app.utils.validation_utils import (
    validate_agent_exists_and_owned,
    validate_user_exists,
)

logger = get_logger(__name__)


def get_all_agents(db: Session, current_user: dict):
    try:
        # --- Validasi user menggunakan utility function ---
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))
        user = validate_user_exists(db, user_id, current_user.get("email"))

        # --- Query agents dengan eager loading ---
        agents = (
            db.query(Agent)
            .filter(Agent.user_id == user.id)
            .options(
                joinedload(Agent.user_agents)
                .joinedload(UserAgent.history_messages)
                .joinedload(HistoryMessage.message_metadata),
                joinedload(Agent.integrations).joinedload(Integration.platform_config),
            )
            .all()
        )

        if not agents:
            logger.info(f"No agents found for user {current_user.get('email')}")
            return []  # frontend dapet array kosong, bukan error

        # --- Format agents summary ---
        agents_summary = []
        for agent in agents:
            # Ambil semua history dari semua user_agents agent ini
            all_histories = []
            for ua in agent.user_agents:
                all_histories.extend(ua.history_messages)

            # Total percakapan
            total_conversations = len(all_histories)

            # Rata-rata response time
            response_times = [
                h.message_metadata.response_time
                for h in all_histories
                if h.message_metadata is not None
            ]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            # Get platform and API key from integrations (prioritize active integrations)
            platform = None
            api_key = None
            if agent.integrations:
                # First try to find an active integration
                active_integration = next(
                    (
                        integration
                        for integration in agent.integrations
                        if integration.status == "active"
                    ),
                    None,
                )
                if active_integration:
                    platform = active_integration.platform
                    # Get API key from platform integration if available
                    if active_integration.platform_config:
                        api_key = active_integration.platform_config.api_key
                else:
                    # If no active integration, take the first one
                    first_integration = agent.integrations[0]
                    platform = first_integration.platform
                    # Get API key from platform integration if available
                    if first_integration.platform_config:
                        api_key = first_integration.platform_config.api_key

            agents_summary.append(
                {
                    "id": agent.id,
                    "avatar": agent.avatar,
                    "name": agent.name,
                    "model": agent.model,
                    "role": agent.role,
                    "status": agent.status,
                    "description": agent.description,
                    "base_prompt": agent.base_prompt,
                    "short_term_memory": agent.short_term_memory,
                    "long_term_memory": agent.long_term_memory,
                    "tone": agent.tone,
                    "platform": platform,
                    "api_key": api_key,
                    "total_conversations": total_conversations,
                    "avg_response_time": round(avg_response_time, 2),
                }
            )

        logger.info(
            f"Successfully retrieved agents for user {current_user.get('email')}"
        )
        return agents_summary

    except HTTPException:
        # biarin lewat kalau memang sudah HTTPException
        raise
    except Exception as e:
        raise handle_database_error(e, "getting agents", current_user.get("email"))


def delete_agent(agent_id: int, current_user: dict, db: Session):
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))
        user = validate_user_exists(db, user_id, current_user.get("email"))

        agent = validate_agent_exists_and_owned(
            db, agent_id, user.id, current_user.get("email")
        )

        # Remove agent from memory if it exists
        try:
            from app.controllers.document_controller import agents

            agent_id_str = str(agent_id)
            if agent_id_str in agents:
                del agents[agent_id_str]
                logger.info(f"Removed agent {agent_id_str} from memory")
        except Exception as memory_error:
            logger.warning(f"Failed to remove agent from memory: {str(memory_error)}")

        # Delete agent (cascade will handle company_information, documents, etc.)
        db.delete(agent)
        db.commit()

        logger.info(
            f"Agent '{agent.name}' (ID: {agent_id}) deleted successfully by user {current_user.get('email')}"
        )
        return {"message": f"delete agent is successfully: agent ID is {agent_id}"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "deleting agent", current_user.get("email"))


def get_all_user_agent(current_user: dict, db: Session):
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))

        # --- Get agents with relationships ---
        agents = (
            db.query(Agent)
            .filter(Agent.user_id == user_id)
            .options(
                joinedload(Agent.user_agents),
                joinedload(Agent.integrations),  # load integrations
            )
            .all()
        )

        # --- Format user agents data menggunakan utility function ---
        result = format_user_agents_data(agents)

        # --- Get user with agents for statistics ---
        user_with_agents = (
            db.query(User)
            .filter(User.id == user_id)
            .options(
                joinedload(User.agents)
                .load_only(Agent.id, Agent.status)
                .joinedload(Agent.user_agents)
                .load_only(UserAgent.id, UserAgent.created_at)
                .joinedload(UserAgent.history_messages)
                .load_only(HistoryMessage.id)
                .joinedload(HistoryMessage.message_metadata)
                .load_only(
                    Metadata.total_tokens,
                    Metadata.response_time,
                    Metadata.is_success,
                )
            )
            .first()
        )

        if not user_with_agents or not user_with_agents.agents:
            logger.info(f"No agents found for user {current_user.get('email')}")
            return {"user_agents": result, "stats": get_default_stats_response()}

        # --- Calculate statistics menggunakan utility function ---
        overview = calculate_agent_statistics(user_with_agents.agents)

        logger.info(
            f"[UserAgents] Fetched {len(result)} user agents for user_id={user_id}"
        )
        return {"user_agents": result, "stats": overview}

    except HTTPException:
        # biarin FastAPI yang handle
        raise
    except Exception as e:
        raise handle_database_error(e, "getting user agents", current_user.get("email"))


async def invoke_agent(
    agent_id: str, agent_invoke: AgentInvoke, current_user: dict, db: Session
):
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))

        get_agent = validate_agent_exists_and_owned(
            db, agent_id, user_id, current_user.get("email")
        )

        agent = agents.get(agent_id, None)
        check_agent_in_redis = await redis_storage.is_agent_exists(agent_id)
        print(f"agent: {agent}")
        if not agent and not check_agent_in_redis:
            logger.warning(f"Agent not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found.",
            )

        elif check_agent_in_redis and not agent:
            from app.utils.agent_utils import build_agent

            await event_bus.publish(
                Event(
                    event_type=EventType.AGENT_INVOKE,
                    user_id=user_id,
                    agent_id=agent_id,
                    payload={"message": "Building the agent..."},
                )
            )
            agent = await build_agent(agent_id)
            logger.info(f"Agent built from redis: {agent}")
            if not agent:
                logger.warning(f"Agent not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found.",
                )

        get_user_agent = (
            db.query(UserAgent).filter(UserAgent.agent_id == agent_id).first()
        )
        if not get_user_agent:
            user_agent = UserAgent(
                id=str(agent_id),
                agent_id=agent_id,
                username="Testing by admin",
                user_platform="api",
            )
            db.add(user_agent)
            db.flush()
            user_agent_id = user_agent.id
        else:
            user_agent_id = get_user_agent.id
        await event_bus.publish(
            Event(
                event_type=EventType.AGENT_INVOKE,
                user_id=user_id,
                agent_id=agent_id,
                payload={"message": "Reasoning..."},
            )
        )
        agent_response = agent.execute(
            {"user_message": agent_invoke.message}, str(agent_id)
        )
        new_history_message = HistoryMessage(
            user_agent_id=user_agent_id,
            user_message=agent_invoke.message,
            response=agent_response.get("response", ""),
        )
        db.add(new_history_message)
        db.flush()
        history_message_id = new_history_message.id
        response_time = agent.response_time
        token_usage = agent.token_usage
        new_metadata = Metadata(
            history_message_id=history_message_id,
            total_tokens=token_usage,
            response_time=response_time,
            model=agent.llm_model,
        )
        db.add(new_metadata)
        db.commit()
        logger.info(
            f"Agent '{get_agent.name}' (ID: {agent_id}) invoked successfully by user {current_user.get('email')}"
        )
        return {
            "user_message": agent_invoke.message,
            "response": agent_response.get("response", ""),
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "invoking agent", current_user.get("email"))
