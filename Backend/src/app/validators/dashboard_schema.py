from typing import List

from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class DashboardOverviewData(BaseModel):
    token_usage: int
    total_conversations: int
    active_agents: int
    average_response_time: float
    success_rate: float


class DashboardOverviewResponse(BaseSchemaOut):
    data: DashboardOverviewData


class TokenUsageTrendItem(BaseModel):
    period: str
    total_tokens: int


class TokenUsageTrendData(BaseModel):
    trend: List[TokenUsageTrendItem]


class TokenUsageTrendResponse(BaseSchemaOut):
    data: TokenUsageTrendData


class ConversationTrendItem(BaseModel):
    period: str
    total_conversations: int


class ConversationTrendData(BaseModel):
    trend: List[ConversationTrendItem]


class ConversationTrendResponse(BaseSchemaOut):
    data: ConversationTrendData


class AgentTokenItem(BaseModel):
    agent_id: str
    agent_name: str
    total_tokens: int


class TotalTokensPerAgentData(BaseModel):
    agents: List[AgentTokenItem]


class TotalTokensPerAgentResponse(BaseSchemaOut):
    data: TotalTokensPerAgentData

