"""
Agent operations utilities
"""
import secrets
import string
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.AI import simple_RAG_agent as AI
from app.controllers.document_controller import agents
from app.models.agent.agent_entity import Agent
from app.models.agent.simple_rag_model import CreateSimpleRAGAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_entity(agent_data_obj: CreateSimpleRAGAgent, user_id: int) -> Agent:
    """
    Create Agent entity from CreateSimpleRAGAgent data
    
    Args:
        agent_data_obj: Agent creation data
        user_id: ID of the user creating the agent
        
    Returns:
        Agent: Created agent entity
    """
    return Agent(
        user_id=user_id,
        name=agent_data_obj.name,
        avatar=agent_data_obj.avatar,
        model=agent_data_obj.model,
        role="simple RAG agent",  # Fixed role for Simple RAG Agent
        description=agent_data_obj.description,
        base_prompt=agent_data_obj.base_prompt,
        tone=agent_data_obj.tone,
        short_term_memory=agent_data_obj.short_term_memory,
        long_term_memory=agent_data_obj.long_term_memory,
        status=agent_data_obj.status,
    )


def initialize_ai_agent(agent: Agent, directory_path: str) -> None:
    """
    Initialize AI agent instance in memory
    
    Args:
        agent: Agent entity
        directory_path: Directory path for agent documents
    """
    agent_id_str = str(agent.id)
    
    if agent_id_str not in agents:
        logger.info(f"Initializing AI agent for agent {agent.id}")
        
        agents[agent_id_str] = AI.Agent(
            base_prompt=str(agent.base_prompt),  # type: ignore
            tone=str(agent.tone),  # type: ignore
            directory_path=directory_path,
            chromadb_path="chroma_db",
            collection_name=f"agent_{agent.id}",
            model_llm=str(agent.model),  # type: ignore
            short_memory=bool(agent.short_term_memory),  # type: ignore
        )
        
        logger.info(f"AI agent initialized for agent {agent.id}")
    else:
        logger.info(f"AI agent already exists for agent {agent.id}")


def add_document_to_agent(agent: Agent, filename: str, content_type: str, document_id: int) -> None:
    """
    Add document to AI agent
    
    Args:
        agent: Agent entity
        filename: Name of the file
        content_type: Type of content (pdf, txt)
        document_id: ID of the document in database
    """
    agent_id_str = str(agent.id)
    
    if agent_id_str in agents:
        agents[agent_id_str].add_document(
            filename,
            content_type,
            str(document_id),
        )
        logger.info(f"Added document {filename} to agent {agent.id}")
    else:
        logger.error(f"AI agent not found for agent {agent.id}")


def build_task_result(agent: Agent, task_id: str, file_data: Optional[Dict] = None, document_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Build task result dictionary
    
    Args:
        agent: Created agent entity
        task_id: Celery task ID
        file_data: Optional file data
        document_id: Optional document ID
        
    Returns:
        Dict[str, Any]: Task result
    """
    result = {
        "status": "completed",
        "agent_id": agent.id,
        "message": "Simple RAG Agent created successfully",
        "task_id": task_id,
    }
    
    # Add file info if file was uploaded
    if file_data:
        result["file_name"] = file_data["filename"]
        if document_id:
            result["document_id"] = document_id
    
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
        if hasattr(agent, 'integrations') and agent.integrations:
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
    active_agents = sum(1 for agent in agents if getattr(agent, 'status', None) == "active")
    
    # Calculate total interactions and tokens
    total_interactions = 0
    total_tokens = 0
    total_response_time = 0
    successful_interactions = 0
    
    for agent in agents:
        if hasattr(agent, 'user_agents') and agent.user_agents:
            for user_agent in agent.user_agents:
                if hasattr(user_agent, 'history_messages') and user_agent.history_messages:
                    for message in user_agent.history_messages:
                        if hasattr(message, 'message_metadata') and message.message_metadata:
                            metadata = message.message_metadata
                            total_interactions += 1
                            
                            if hasattr(metadata, 'total_tokens') and metadata.total_tokens:
                                total_tokens += metadata.total_tokens
                            
                            if hasattr(metadata, 'response_time') and metadata.response_time:
                                total_response_time += metadata.response_time
                            
                            if hasattr(metadata, 'is_success') and metadata.is_success:
                                successful_interactions += 1
    
    # Calculate averages
    avg_response_time = total_response_time / total_interactions if total_interactions > 0 else 0
    success_rate = (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
    
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


def generate_api_key(db: Session, user_id: int, agent_id: int) -> str:
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
    api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # Create API key record
    api_key_record = ApiKey(
        user_id=user_id,
        agent_id=agent_id,
        key=api_key,
        is_active=True
    )
    
    db.add(api_key_record)
    db.flush()
    
    logger.info(f"Generated API key for user {user_id}, agent {agent_id}")
    return api_key


def validate_api_key(api_key: str, db: Session, agent_id: int) -> bool:
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
        # Use raw SQL to avoid SQLAlchemy boolean issues
        result = db.execute(
            text("SELECT * FROM api_keys WHERE key = :key AND agent_id = :agent_id AND is_active = true"),
            {"key": api_key, "agent_id": agent_id}
        ).fetchone()
        
        api_key_record = result if result else None
        
        if api_key_record:
            logger.info(f"Valid API key for agent {agent_id}")
            return True
        else:
            logger.warning(f"Invalid API key for agent {agent_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False