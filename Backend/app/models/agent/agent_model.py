from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, EmailStr


class AgentBase(BaseModel):
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    role: Optional[
        Literal[
            "simple RAG agent",
            "customer service",
            "data analyst",
            "finance assistant",
            "sales",
        ]
    ] = None
    description: Optional[str] = None
    tone: Optional[Literal["formal", "friendly", "casual", "profesional"]] = None


class CreateAgent(AgentBase):
    base_prompt: Optional[str] = "Tidak ada base prompt tambahan"
    status: Literal["active", "non-active"]
    short_term_memory: bool = False
    long_term_memory: Optional[bool] = False


class GettingAllAgents(AgentBase):
    short_term_memory: bool
    long_term_memory: bool
    status: Literal["active", "non-active"]
    created_at: datetime


class AgentOut(AgentBase):
    id: int
    status: Literal["active", "non-active"]


class ResponseAPI(BaseModel):
    status: str
    message: str
    data: AgentOut


class UpdateAgent(BaseModel):
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    description: Optional[str] = None
    base_prompt: Optional[str] = None
    tone: Optional[Literal["formal", "friendly", "casual", "profesional"]] = None
    short_term_memory: Optional[bool] = False
    long_term_memory: Optional[bool] = False
    status: Optional[Literal["active", "non-active"]]

class AgentInvoke(BaseModel):
    message:str