from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

from src.app.validators.base import BasePaginateOut, BaseSchemaOut


class BaseAgentSchema(BaseModel):
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
    description: Optional[str] = None
    status: Literal["active", "non-active"]
    base_prompt: str
    short_term_memory: bool
    long_term_memory: bool
    tone: str
    created_at: Optional[datetime] = None


class CreateAgent(BaseAgentSchema):
    llm_provider: str

    class Config:
        orm_mode = True

    def to_dict(self, *, exclude_none: bool = True, by_alias: bool = False):
        data = self.dict(by_alias=by_alias, exclude_none=exclude_none)
        if data.get("created_at") and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data


class CreateAgentOut(BaseAgentSchema):
    id: str


class CreateAgentResponse(BaseSchemaOut):
    data: CreateAgentOut


class AgentPaginate(BaseAgentSchema):
    id: str
    user_id: int


class AgentPaginateOut(BasePaginateOut):
    data_agents: List[AgentPaginate]


class AgentPaginateResponse(BaseSchemaOut):
    data: AgentPaginateOut


class AgentDetailSchema(BaseAgentSchema):
    id: str
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


class InvokeAgentRequest(BaseModel):
    message: str
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how can you help me?",
                "username": "john_doe",
                "user_platform": "api",
            }
        }


class InvokeAgentResponseData(BaseModel):
    user_message: str
    response: str
    total_tokens: int | float
    response_time: int | float


class InvokeAgentResponse(BaseSchemaOut):
    data: InvokeAgentResponseData
