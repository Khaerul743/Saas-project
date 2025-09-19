from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class CustomerServiceAgentBase(BaseModel):
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    description: Optional[str] = None
    base_prompt: str  # Required for Customer Service Agent
    tone: Literal["formal", "friendly", "casual", "profesional"]
    short_term_memory: bool = False
    long_term_memory: bool = True  # Usually enabled for customer service
    status: Literal["active", "non-active"]


class CreateCustomerServiceAgent(CustomerServiceAgentBase):
    """Model for creating a Customer Service Agent"""
    pass


class CustomerServiceAgentOut(CustomerServiceAgentBase):
    id: int
    created_at: datetime


class UpdateCustomerServiceAgent(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    model: Optional[Literal["gpt-3.5-turbo", "gpt-4o"]] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None
    tone: Optional[Literal["formal", "friendly", "casual", "profesional"]] = None
    short_term_memory: Optional[bool] = None
    long_term_memory: Optional[bool] = None
    status: Optional[Literal["active", "non-active"]] = None


class CustomerServiceAgentResponse(BaseModel):
    status: str
    message: str
    data: CustomerServiceAgentOut


class DatasetDescription(BaseModel):
    """Model for dataset description"""
    filename: str = Field(..., description="Name of the dataset file (without extension)")
    description: str = Field(..., description="Description of the dataset content and purpose")


class CustomerServiceAgentCreateRequest(BaseModel):
    """Complete request model for creating Customer Service Agent"""
    agent_data: CreateCustomerServiceAgent
    datasets: List[DatasetDescription] = Field(
        default_factory=list, 
        description="List of dataset descriptions for CSV/Excel files"
    )
