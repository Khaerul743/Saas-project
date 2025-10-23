"""
Utility functions for calculations and data processing.
"""

from typing import Dict, List, Any

from app.models.agent.agent_entity import Agent
from app.core.logger import get_logger

logger = get_logger(__name__)


def calculate_dashboard_overview(agents: List[Agent]) -> Dict[str, Any]:
    """
    Calculate dashboard overview statistics from a list of agents.

    Args:
        agents: List of Agent objects with loaded relationships

    Returns:
        Dictionary containing dashboard overview statistics
    """
    total_tokens = 0
    total_conversations = 0
    active_agents = 0
    response_times = []
    success_count = 0

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
        (success_count / total_conversations) * 100 if total_conversations > 0 else 0
    )

    return {
        "token_usage": total_tokens,
        "total_conversations": total_conversations,
        "active_agents": active_agents,
        "average_response_time": round(avg_response_time, 2),
        "success_rate": round(success_rate, 2),
    }


def format_token_usage_trend_data(results: List) -> List[Dict[str, Any]]:
    """
    Format token usage trend data from database query results.

    Args:
        results: Raw query results from database

    Returns:
        List of dictionaries containing period and total_tokens
    """
    trend = []
    for r in results:
        period = r.period
        period_str = period.isoformat() if hasattr(period, "isoformat") else str(period)

        trend.append({"period": period_str, "total_tokens": int(r.total_tokens or 0)})

    return trend


def format_conversation_trend_data(results: List) -> List[Dict[str, Any]]:
    """
    Format conversation trend data from database query results.

    Args:
        results: Raw query results from database

    Returns:
        List of dictionaries containing period and total_conversations
    """
    trend = [
        {
            "period": str(r.period.date() if hasattr(r.period, "date") else r.period),
            "total_conversations": int(r.total_conversations or 0),
        }
        for r in results
    ]

    return trend


def format_total_tokens_per_agent_data(results: List) -> List[Dict[str, Any]]:
    """
    Format total tokens per agent data from database query results.

    Args:
        results: Raw query results from database

    Returns:
        List of dictionaries containing agent_id, agent_name, and total_tokens
    """
    agents_tokens = [
        {
            "agent_id": r.agent_id,
            "agent_name": r.agent_name,
            "total_tokens": int(r.total_tokens or 0),
        }
        for r in results
    ]

    return agents_tokens


def get_default_dashboard_response() -> Dict[str, Any]:
    """
    Get default dashboard response when no agents are found.

    Returns:
        Default dashboard statistics dictionary
    """
    return {
        "token_usage": 0,
        "total_conversations": 0,
        "active_agents": 0,
        "average_response_time": 0,
        "success_rate": 0,
    }
