from typing import Optional
from pydantic import BaseModel

class CreateCompanyInformation(BaseModel):
    # Basic Company Information
    name: str
    industry: str
    description: str
    address: str
    email: str
    website: Optional[str] = None
    fallback_email: str


class UpdateCompanyInformation(BaseModel):
    # Basic Company Information - all optional for partial updates
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    fallback_email: Optional[str] = None


class CompanyInformationOut(BaseModel):
    id: int
    agent_id: int
    name: str
    industry: str
    description: str
    address: str
    email: str
    website: Optional[str] = None
    fallback_email: str
    created_at: str

    class Config:
        from_attributes = True


