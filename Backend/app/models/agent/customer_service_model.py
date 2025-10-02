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
    long_term_memory: bool = False  # Usually enabled for customer service
    status: Literal["active", "non-active"]


class CreateCustomerServiceAgent(CustomerServiceAgentBase):
    """Model for creating a Customer Service Agent"""
    company_name: str
    industry: str
    company_description: str
    address: str
    email: str
    website: Optional[str] = None
    fallback_email: str


class CustomerServiceAgentOut(CustomerServiceAgentBase):
    id: int
    created_at: datetime


class CustomerServiceAgentAsyncResponse(BaseModel):
    """Response model for async Customer Service Agent creation"""
    id: Optional[int] = None
    name: str
    avatar: Optional[str] = None
    model: Literal["gpt-3.5-turbo", "gpt-4o"]
    description: Optional[str] = None
    base_prompt: str
    tone: Literal["formal", "friendly", "casual", "profesional"]
    short_term_memory: bool = False
    long_term_memory: bool = False
    status: Literal["active", "non-active", "pending"]  # Add pending status
    created_at: Optional[datetime] = None
    task_id: str
    message: str


class UpdateCustomerServiceAgent(BaseModel):
    # Agent fields
    name: Optional[str] = None
    avatar: Optional[str] = None
    model: Optional[Literal["gpt-3.5-turbo", "gpt-4o"]] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None
    tone: Optional[Literal["formal", "friendly", "casual", "profesional"]] = None
    short_term_memory: Optional[bool] = None
    long_term_memory: Optional[bool] = None
    status: Optional[Literal["active", "non-active"]] = None
    
    # Company information fields
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_description: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    fallback_email: Optional[str] = None


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

    

