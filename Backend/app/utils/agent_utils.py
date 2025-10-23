"""
Agent operations utilities
"""

import json
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import WebSocket
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.AI import customer_service as CustomerServiceAI
from app.AI import simple_RAG_agent as SimpleRAGAI
from app.controllers.document_controller import agents
from app.dependencies.redis_storage import redis_storage
from app.models.agent.agent_entity import Agent
from app.models.agent.simple_rag_model import CreateSimpleRAGAgent
from app.models.company_information.company_entity import CompanyInformation
from app.models.company_information.company_model import CreateCompanyInformation
from app.models.document.document_entity import Document
from app.models.history_message.history_entity import HistoryMessage
from app.models.history_message.metadata_entity import Metadata
from app.models.integration.integration_entity import Integration
from app.models.platform.platform_entity import Platform
from app.models.user.api_key_entity import ApiKey
from app.models.user.user_entity import User
from app.models.user_agent.user_agent_entity import UserAgent
from app.core.logger import get_logger
from app.websocket.manager import ws_manager

logger = get_logger(__name__)


async def build_agent(agent_id: str):
    get_agent = await redis_storage.get_agent(agent_id)
    if get_agent:
        if get_agent["role"] == "simple RAG agent":
            agent = SimpleRAGAI.Agent(
                base_prompt=get_agent["base_prompt"],
                tone=get_agent["tone"],
                directory_path=get_agent["directory_path"],
                chromadb_path=get_agent["chromadb_path"],
                collection_name=get_agent["collection_name"],
                model_llm=get_agent["model_llm"],
                short_memory=get_agent["short_memory"],
            )
            agents[agent_id] = agent
        elif get_agent["role"] == "customer service agent":
            company_information = CreateCompanyInformation(
                name=get_agent["company_information"]["name"],
                industry=get_agent["company_information"]["industry"],
                description=get_agent["company_information"]["description"],
                address=get_agent["company_information"]["address"],
                email=get_agent["company_information"]["email"],
                website=get_agent["company_information"]["website"],
                fallback_email=get_agent["company_information"]["fallback_email"],
            )
            agent = CustomerServiceAI.Agent(
                base_prompt=get_agent["base_prompt"],
                tone=get_agent["tone"],
                llm_model=get_agent["llm_model"],
                directory_path=get_agent["directory_path"],
                chromadb_path=get_agent["chromadb_path"],
                collection_name=get_agent["collection_name"],
                available_databases=get_agent["available_databases"],
                detail_data=get_agent["detail_data"],
                company_information=company_information,
                long_memory=get_agent["long_memory"],
                short_memory=get_agent["short_memory"],
                status=get_agent["status"],
                **get_agent["dataset_descriptions"],
            )
            agents[agent_id] = agent
        else:
            raise Exception("Agent not found")
        return agent
    else:
        return None


# app/websocket/agent_websocket_utils.py


async def invoke_agent_logic(
    user_id: str,
    agent_id: str,
    user_message: str,
    db: Session,
    generate_id="",
    include_ws: bool = False,
):
    """
    Helper function untuk invoke agent logic yang bisa digunakan di WebSocket
    """
    try:
        # Check if agent exists in memory
        agent = agents.get(str(agent_id))
        check_agent_in_redis = await redis_storage.is_agent_exists(agent_id)

        if not agent and check_agent_in_redis:
            from app.utils.agent_utils import build_agent

            if include_ws:
                await ws_manager.send_to_user(
                    f"invoke_agent_{str(user_id)}",
                    {
                        "type": "progress",
                        "message": "Building the agent...",
                    },
                )
            agent = await build_agent(agent_id)

        if not agent:
            raise Exception("Agent not found")

        # Execute agent
        agent_response = agent.execute(
            {
                "user_message": user_message,
                "include_ws": include_ws,
                "user_id": user_id,
            },
            str(agent_id + generate_id),
        )

        return {
            "response": agent_response.get("response", ""),
            "token_usage": getattr(agent, "token_usage", 0),
            "response_time": getattr(agent, "response_time", 0),
            "model": getattr(agent, "llm_model", "unknown"),
        }

    except Exception as e:
        logger.error(f"Error in agent logic: {e}")

        raise e


def generate_agent_id(db: Session):
    """
    Generate a unique agent ID with improved collision handling

    Args:
        db: Database session

    Returns:
        str: Unique agent ID
    """
    import time

    max_attempts = 10

    for attempt in range(max_attempts):
        # Generate ID with timestamp component to reduce collision probability
        timestamp_suffix = str(int(time.time() * 1000))[
            -3:
        ]  # Last 3 digits of timestamp
        random_part = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(2)
        )
        id = random_part + timestamp_suffix

        # Check if ID exists
        is_exists = db.query(Agent).filter(Agent.id == id).first()
        if not is_exists:
            return id

        # If collision occurs, wait a bit and try again
        time.sleep(0.001)  # 1ms delay

    # Fallback: use UUID if all attempts fail
    import uuid

    return str(uuid.uuid4())[:8]


def create_agent_entity(agent_data_obj, user_id: int, agent_role: str) -> Agent:
    """
    Create Agent entity

    Args:
        agent_data_obj: Agent creation data
        user_id: ID of the user creating the agent

    Returns:
        Agent: Created agent entity
    """
    return Agent(
        id=agent_data_obj.id,
        user_id=user_id,
        name=agent_data_obj.name,
        avatar=agent_data_obj.avatar,
        model=agent_data_obj.model,
        role=agent_role,
        description=agent_data_obj.description,
        base_prompt=agent_data_obj.base_prompt,
        tone=agent_data_obj.tone,
        short_term_memory=agent_data_obj.short_term_memory,
        long_term_memory=agent_data_obj.long_term_memory,
        status=agent_data_obj.status,
    )


def initialize_simple_rag_agent(agent: Agent, directory_path: str):
    """
    Initialize AI agent instance in memory

    Args:
        agent: Agent entity
        directory_path: Directory path for agent documents
    """
    agent_id_str = str(agent.id)

    if not agent_id_str in agents:
        logger.info(f"Initializing AI agent for agent {agent.id}")

        agent_obj = SimpleRAGAI.Agent(
            base_prompt=str(agent.base_prompt),  # type: ignore
            tone=str(agent.tone),  # type: ignore
            directory_path=directory_path,
            chromadb_path="chroma_db",
            collection_name=f"agent_{agent.id}",
            model_llm=str(agent.model),  # type: ignore
            short_memory=bool(agent.short_term_memory),  # type: ignore
        )
        agents[agent_id_str] = agent_obj
        logger.info(f"AI agent initialized for agent {agent.id}")
        print(f"=================================================")
        print(f"agents: {agents}")
        print(f"=================================================")
    else:
        logger.info(f"AI agent already exists for agent {agent.id}")


def initialize_customer_service_agent(
    agent: Agent, directory_path: str, agent_data_obj, datasets: List[dict]
):
    """
    Initialize Customer Service AI agent instance in memory

    Args:
        agent: Agent entity
        directory_path: Directory path for agent documents
        agent_data_obj: Customer Service Agent creation data
        datasets: List of dataset descriptions
    """
    agent_id_str = str(agent.id)

    if agent_id_str not in agents:
        logger.info(f"Initializing Customer Service AI agent for agent {agent.id}")

        # Prepare dataset descriptions
        dataset_descriptions = {}
        available_databases = []
        detail_data_parts = []

        # Process datasets
        for dataset in datasets:
            if dataset.get("filename"):
                filename_without_ext = dataset["filename"]
                available_databases.append(filename_without_ext)
                dataset_descriptions[f"db_{filename_without_ext}_description"] = (
                    dataset.get("description", "")
                )

        # Create company information
        from app.models.company_information.company_model import (
            CreateCompanyInformation,
        )

        company_information = CreateCompanyInformation(
            name=agent_data_obj.company_name,
            industry=agent_data_obj.industry,
            description=agent_data_obj.company_description,
            address=agent_data_obj.address,
            email=agent_data_obj.email,
            website=agent_data_obj.website,
            fallback_email=agent_data_obj.fallback_email,
        )

        # Initialize Customer Service Agent
        customer_service_agent = CustomerServiceAI.Agent(
            base_prompt=str(agent.base_prompt),
            tone=str(agent.tone),
            llm_model=str(agent.model),
            directory_path=directory_path,
            chromadb_path="chroma_db",
            collection_name=f"agent_{agent.id}",
            available_databases=available_databases,
            detail_data="\n".join(detail_data_parts) if detail_data_parts else "",
            company_information=company_information,
            long_memory=bool(agent.long_term_memory),
            short_memory=bool(agent.short_term_memory),
            status="active",
            **dataset_descriptions,
        )
        agents[agent_id_str] = customer_service_agent  # type: ignore
        logger.info(f"Customer Service AI agent initialized for agent {agent.id}")
        return customer_service_agent
    else:
        logger.info(f"Customer Service AI agent already exists for agent {agent.id}")


def add_document_to_agent(
    agent_id: str,
    filename: str,
    content_type: str,
    document_id: int,
    directory_path: str,
) -> None:
    """
    Add document to AI agent

    Args:
        agent_id: Agent ID
        filename: Name of the file
        content_type: Type of content (pdf, txt)
        document_id: ID of the document in database
    """

    agent_id_str = str(agent_id)
    from app.AI.document_store.RAG import RAGSystem

    rag = RAGSystem(
        chroma_directiory="chroma_db", collection_name=f"agent_{agent_id_str}"
    )
    rag.add_document_collection(
        directory_path=directory_path,
        file_name=filename,
        file_type=content_type,
        doc_id=str(document_id),
    )
    logger.info(f"Added document {filename} to agent {agent_id_str}")
    print(f"=================================================")
    print(f"Added document {filename} to agent {agent_id_str}")
    print(f"directory_path: {directory_path}")
    print(f"collection_name: {f'agent_{agent_id_str}'}")
    print(f"=================================================")


def build_task_result(
    agent: Agent,
    task_id: str,
    file_data: Optional[Dict] = None,
    document_id: Optional[int] = None,
    document_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Build task result dictionary

    Args:
        agent: Created agent entity
        task_id: Celery task ID
        file_data: Optional file data
        document_id: Optional document ID
        document_ids: Optional list of document IDs

    Returns:
        Dict[str, Any]: Task result
    """
    result = {
        "status": "completed",
        "agent_id": agent.id,
        "message": f"{agent.role.title()} Agent created successfully",
        "task_id": task_id,
    }

    # Add file info if file was uploaded
    if file_data:
        result["file_name"] = file_data["filename"]
        if document_id:
            result["document_id"] = document_id
        if document_ids:
            result["document_ids"] = document_ids

    return result


def format_user_agents_data(agents: List[Agent]) -> List[Dict[str, Any]]:
    """
    Format user agents data for API response

    Args:
        agents: List of Agent entities

    Returns:
        List[Dict[str, Any]]: Formatted agents data
    """
    result = []

    for agent in agents:
        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "avatar": agent.avatar,
            "model": agent.model,
            "role": agent.role,
            "description": agent.description,
            "status": agent.status,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,  # type: ignore
        }

        # Add integrations if available
        if hasattr(agent, "integrations") and agent.integrations:
            agent_data["integrations"] = [
                {
                    "id": integration.id,
                    "platform": integration.platform,
                    "status": integration.status,
                }
                for integration in agent.integrations
            ]

        result.append(agent_data)

    return result


def calculate_agent_statistics(agents: List[Agent]) -> Dict[str, Any]:
    """
    Calculate agent statistics from user agents

    Args:
        agents: List of Agent entities

    Returns:
        Dict[str, Any]: Calculated statistics
    """
    if not agents:
        return get_default_stats_response()

    total_agents = len(agents)
    active_agents = sum(
        1 for agent in agents if getattr(agent, "status", None) == "active"
    )

    # Calculate total interactions and tokens
    total_interactions = 0
    total_tokens = 0
    total_response_time = 0
    successful_interactions = 0

    for agent in agents:
        if hasattr(agent, "user_agents") and agent.user_agents:
            for user_agent in agent.user_agents:
                if (
                    hasattr(user_agent, "history_messages")
                    and user_agent.history_messages
                ):
                    for message in user_agent.history_messages:
                        if (
                            hasattr(message, "message_metadata")
                            and message.message_metadata
                        ):
                            metadata = message.message_metadata
                            total_interactions += 1

                            if (
                                hasattr(metadata, "total_tokens")
                                and metadata.total_tokens
                            ):
                                total_tokens += metadata.total_tokens

                            if (
                                hasattr(metadata, "response_time")
                                and metadata.response_time
                            ):
                                total_response_time += metadata.response_time

                            if hasattr(metadata, "is_success") and metadata.is_success:
                                successful_interactions += 1

    # Calculate averages
    avg_response_time = (
        total_response_time / total_interactions if total_interactions > 0 else 0
    )
    success_rate = (
        (successful_interactions / total_interactions * 100)
        if total_interactions > 0
        else 0
    )

    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_interactions": total_interactions,
        "total_tokens": total_tokens,
        "avg_response_time": round(avg_response_time, 2),
        "success_rate": round(success_rate, 2),
    }


def get_default_stats_response() -> Dict[str, Any]:
    """
    Get default statistics response when no agents found

    Returns:
        Dict[str, Any]: Default statistics
    """
    return {
        "total_agents": 0,
        "active_agents": 0,
        "total_interactions": 0,
        "total_tokens": 0,
        "avg_response_time": 0.0,
        "success_rate": 0.0,
    }


def generate_api_key(db: Session, user_id: int, agent_id: str) -> str:
    """
    Generate a new API key for agent

    Args:
        db: Database session
        user_id: ID of the user
        agent_id: ID of the agent

    Returns:
        str: Generated API key
    """
    from app.models.user.api_key_entity import ApiKey

    # Generate a secure random API key
    alphabet = string.ascii_letters + string.digits
    api_key = "".join(secrets.choice(alphabet) for _ in range(32))

    # Create API key record (30 days expiration)
    api_key_record = ApiKey(
        user_id=user_id,
        agent_id=agent_id,
        api_key=api_key,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )

    db.add(api_key_record)
    db.flush()

    logger.info(f"Generated API key for user {user_id}, agent {agent_id}")
    return api_key


def validate_api_key(api_key: str, db: Session, agent_id: str) -> bool:
    """
    Validate API key for agent

    Args:
        api_key: API key to validate
        db: Database session
        agent_id: ID of the agent

    Returns:
        bool: True if API key is valid, False otherwise
    """
    from app.models.user.api_key_entity import ApiKey

    try:
        # ORM validation: match api_key and agent_id, and not expired
        api_key_record = (
            db.query(ApiKey)
            .filter(
                ApiKey.api_key == api_key,
                ApiKey.agent_id == agent_id,
                ApiKey.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if api_key_record:
            logger.info(f"Valid API key for agent {agent_id}")
            return True
        else:
            logger.warning(f"Invalid or expired API key for agent {agent_id}")
            return False

    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False
