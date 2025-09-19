from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class SimpleRAGAgentBase(BaseModel):
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    description: Optional[str] = None
    base_prompt: str  # Required for Simple RAG Agent
    tone: Literal["formal", "friendly", "casual", "profesional"]
    short_term_memory: bool = False
    long_term_memory: bool = False
    status: Literal["active", "non-active"]


class CreateSimpleRAGAgent(SimpleRAGAgentBase):
    """Model for creating a Simple RAG Agent"""
    pass


class SimpleRAGAgentOut(SimpleRAGAgentBase):
    id: int
    created_at: datetime


class UpdateSimpleRAGAgent(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    model: Optional[Literal["gpt-3.5-turbo", "gpt-4o"]] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None
    tone: Optional[Literal["formal", "friendly", "casual", "profesional"]] = None
    short_term_memory: Optional[bool] = None
    long_term_memory: Optional[bool] = None
    status: Optional[Literal["active", "non-active"]] = None


class SimpleRAGAgentResponse(BaseModel):
    status: str
    message: str
    data: SimpleRAGAgentOut
