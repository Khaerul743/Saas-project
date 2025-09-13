import os
import shutil
from typing import List

from fastapi import BackgroundTasks, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.query import Query

from app.AI import simple_RAG_agent as AI
from app.controllers.document_controller import agents
from app.models.agent.agent_entity import Agent
from app.models.agent.agent_model import (
    AgentOut,
    CreateAgent,
    GettingAllAgents,
    UpdateAgent,
)
from app.models.document.document_entity import Document
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.integration.integration_entity import Integration
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.utils.logger import get_logger
from app.utils.agent_utils import (
    calculate_agent_statistics,
    format_user_agents_data,
    get_default_stats_response,
)
from app.utils.error_utils import (
    handle_database_error,
    handle_user_not_found,
    handle_agent_not_found,
)
from app.utils.validation_utils import (
    validate_user_exists,
    validate_agent_exists_and_owned,
)
from app.utils.document_utils import write_document
logger = get_logger(__name__)


def get_all_agents(db: Session, current_user: dict):
    try:
        # --- Validasi user menggunakan utility function ---
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))

        # --- Query agents dengan eager loading ---
        agents = (
            db.query(Agent)
            .filter(Agent.user_id == user.id)
            .options(
                joinedload(Agent.user_agents)
                .joinedload(UserAgent.history_messages)
                .joinedload(HistoryMessage.message_metadata),
                joinedload(Agent.integrations)
                .joinedload(Integration.telegram),
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
                    # Get API key from telegram integration if available
                    if active_integration.telegram:
                        api_key = active_integration.telegram.api_key
                else:
                    # If no active integration, take the first one
                    first_integration = agent.integrations[0]
                    platform = first_integration.platform
                    # Get API key from telegram integration if available
                    if first_integration.telegram:
                        api_key = first_integration.telegram.api_key

            agents_summary.append(
                {
                    "id": agent.id,
                    "avatar": agent.avatar,
                    "name": agent.name,
                    "model": agent.model,
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
        raise handle_database_error(e, "getting agents", current_user.get('email'))


async def create_agent(
    db: Session,
    file,
    agent_data: CreateAgent,
    current_user: dict,
    background_tasks: BackgroundTasks,
) -> AgentOut:
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
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))

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
            status=agent_data.status,
            base_prompt=agent_data.base_prompt or "Tidak ada base prompt tambahan",
        )

        # Add to database
        db.add(new_agent)
        db.flush()

        directory_path = f"documents/user_{current_user.get('id')}/agent_{new_agent.id}"
        if not str(new_agent.id) in agents:

            def init_agent():
                agents[str(new_agent.id)] = AI.Agent(
                    base_prompt=new_agent.base_prompt,
                    tone=new_agent.tone,
                    directory_path=directory_path,
                    chromadb_path="chroma_db",
                    collection_name=f"agent_{new_agent.id}",
                    model_llm=new_agent.model,
                    short_memory=agent_data.short_term_memory,
                )
                # agents[str(new_agent.id)].execute(
                #     {"user_message": "hai", "base_prompt": new_agent.base_prompt, "tone": new_agent.tone},
                #     "thread_123",
                # )

            init_agent()
       
        if file:
            # if file.content_type == "application/pdf":
            #     content_type = "pdf"
            # elif file.content_type == "application/txt":
            #     content_type = "txt"
            # else:
            #     content_type = "docs"
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail="File type must be pdf or txt.",
            #     )
            # if not os.path.exists(directory_path):
            #     os.makedirs(directory_path, exist_ok=True)
            # file_path = os.path.join(directory_path, file.filename)
            # with open(file_path, "wb") as buffer:
            #     shutil.copyfileobj(file.file, buffer)
            content_type = write_document(file, directory_path)
            post_document = Document(
                agent_id=new_agent.id,
                file_name=file.filename,
                content_type=content_type,
            )

            db.add(post_document)
            db.flush()
            agents[str(new_agent.id)].add_document(
                file.filename,
                content_type,
                str(post_document.id),
                db,
                post_document,
                f"{directory_path}/{file.filename}",
            )

            db.commit()
            db.refresh(post_document)

            logger.info(
                f"Agent '{new_agent.name}' (ID: {new_agent.id}) document store successfully by user "
                f"{current_user.get('email')}"
            )
        else:
            db.commit()

        # Log successful creation
        logger.info(
            f"Agent '{new_agent.name}' created successfully by user {current_user.get('email')} "
            f"(user_id: {user.id}, agent_id: {new_agent.id})"
        )
        # Return agent data in expected format
        return AgentOut(
            id=new_agent.id,
            name=new_agent.name,
            avatar=new_agent.avatar or "",
            model=new_agent.model,
            role=new_agent.role,
            description=new_agent.description or "",
            tone=new_agent.tone,
            status="active",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "creating agent", current_user.get('email'))


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
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))

        # Get agent and verify ownership
        agent = validate_agent_exists_and_owned(db, agent_id, user.id, current_user.get('email'))
        this_agent = agents[str(agent_id)]
        if not this_agent:
            logger.warning(
                f"Agent not found: agent_id {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )
        
        # Update agent properties using the new methods
        if agent_data.base_prompt is not None:
            this_agent.update_base_prompt(agent_data.base_prompt)
        if agent_data.tone is not None:
            this_agent.update_tone(agent_data.tone)
        if agent_data.short_term_memory is not None:
            this_agent.update_short_memory(agent_data.short_term_memory)
        
        print(f"model: {this_agent.llm_model}")
        print(f"base_prompt: {this_agent.base_prompt}")
        print(f"tone: {this_agent.tone}")
        print(f"short_memory: {this_agent.short_memory}")
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
            id=agent.id,
            name=agent.name,
            avatar=agent.avatar or "",
            model=agent.model,
            description=agent.description or "",
            tone=agent.tone,
            status=agent.status,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "updating agent", current_user.get('email'))


def delete_agent(agent_id: int, current_user: dict, db: Session):
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        user = validate_user_exists(db, user_id, current_user.get('email'))

        agent = validate_agent_exists_and_owned(db, agent_id, user.id, current_user.get('email'))

        db.delete(agent)
        db.commit()
        return {"message": f"delete agent is successfully: agent ID is {agent_id}"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        db.rollback()
        raise handle_database_error(e, "deleting agent", current_user.get('email'))

def get_all_user_agent(current_user: dict, db: Session):
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get('email', 'unknown'))
        
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
            return {
                "user_agents": result,
                "stats": get_default_stats_response()
            }

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
        raise handle_database_error(e, "getting user agents", current_user.get('email'))