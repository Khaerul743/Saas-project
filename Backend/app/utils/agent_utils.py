"""
Utility functions for agent-related operations and statistics.
"""

from typing import Dict, List, Any

from app.models.agent.agent_entity import Agent
from sqlalchemy.orm import Session
from app.models.user.user_entity import User
from app.utils.logger import get_logger
import secrets
from app.models.user.api_key_entity import ApiKey
logger = get_logger(__name__)
from datetime import datetime, timedelta

def calculate_agent_statistics(agents: List[Agent]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of agents.
    
    Args:
        agents: List of Agent objects with loaded relationships
        
    Returns:
        Dictionary containing agent statistics
    """
    total_conversations = 0
    response_times = []
    success_count = 0
    total_tokens = 0
    active_agents = 0
    
    for agent in agents:
        if agent.status == "active":
            active_agents += 1
            
        for ua in agent.user_agents:
            for history in ua.history_messages:
                total_conversations += 1
                metadata = history.message_metadata
                if metadata:
                    total_tokens += metadata.total_tokens or 0
                    if metadata.response_time is not None:
                        response_times.append(metadata.response_time)
                    if metadata.is_success:
                        success_count += 1
    
    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )
    success_rate = (
        (success_count / total_conversations) * 100
        if total_conversations > 0
        else 0
    )
    
    return {
        "token_usage": total_tokens,
        "total_conversations": total_conversations,
        "active_agents": active_agents,
        "average_response_time": round(avg_response_time, 2),
        "success_rate": round(success_rate, 2),
    }


def format_user_agents_data(agents: List[Agent]) -> List[Dict[str, Any]]:
    """
    Format user agents data for API response.
    
    Args:
        agents: List of Agent objects with loaded relationships
        
    Returns:
        List of formatted user agent dictionaries
    """
    result = []
    
    for agent in agents:
        # Get platform from integrations (safe if integrations is empty)
        platform = agent.integrations[0].platform if agent.integrations else None
        
        for ua in agent.user_agents:
            result.append({
                "agent_name": agent.name,
                "agent_id": ua.agent_id,
                "username": ua.username,
                "user_agent_id": ua.id,
                "platform": platform,
                "created_at": ua.created_at,
            })
    
    return result


def get_default_stats_response() -> Dict[str, Any]:
    """
    Get default statistics response when no agents are found.
    
    Returns:
        Default statistics dictionary
    """
    return {
        "token_usage": 0,
        "total_conversations": 0,
        "active_agents": 0,
        "average_response_time": 0,
        "success_rate": 0,
    }

def generate_api_key(db:Session, user_id: int, agent_id: int) -> str:
    """
    Generate a random API key.
    """
    api_key = secrets.token_hex(32)
    new_api_key = ApiKey(
        user_id=user_id,
        agent_id=agent_id,
        api_key=api_key,
        expires_at=datetime.now() + timedelta(days=30),
    )
    db.add(new_api_key)
    db.commit()
    return api_key


def validate_api_key(api_key: str, db:Session, agent_id: int) -> bool:
    """
    Validate an API key.
    """

    api_key = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.expires_at > datetime.now(), ApiKey.agent_id == agent_id).first()
    if not api_key:
        return False
    return True

