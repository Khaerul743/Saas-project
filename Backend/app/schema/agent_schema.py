from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

from app.schema.base import BasePaginateOut, BaseSchemaOut


class BaseAgentSchema(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    role: Literal[
        "simple RAG agent",
        "customer service",
        "data analyst",
        "finance assistant",
        "sales",
    ]
    description: str
    status: Literal["active", "non-active"]
    base_prompt: str
    short_term_memory: bool
    long_term_memory: bool
    tone: str
    created_at: datetime


class AgentPaginate(BaseAgentSchema):
    user_id: int


class AgentPaginateOut(BasePaginateOut):
    data_agents: List[AgentPaginate]


class AgentPaginateResponse(BaseSchemaOut):
    data: AgentPaginateOut


class AgentDetailSchema(BaseAgentSchema):
    platform: Optional[str] = None
    api_key: Optional[str] = None
    total_conversations: int
    avg_response_time: float


class AgentDetailResponse(BaseSchemaOut):
    data: List[AgentDetailSchema]


class AgentDeleteResponse(BaseSchemaOut):
    data: BaseAgentSchema


class UserAgentSchema(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    role: Literal[
        "simple RAG agent",
        "customer service",
        "data analyst",
        "finance assistant",
        "sales",
    ]
    description: str
    status: Literal["active", "non-active"]
    created_at: datetime
    integrations: Optional[List[dict]] = None


class AgentStatsSchema(BaseModel):
    total_agents: int
    active_agents: int
    total_interactions: int
    total_tokens: int
    avg_response_time: float
    success_rate: float


class UserAgentResponse(BaseSchemaOut):
    data: dict