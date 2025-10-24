from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel, EmailStr


# Base schema (shared attributes)
class UserBase(BaseModel):
    name: str
    email: EmailStr
    company_name: str
    plan: Literal["free", "normal", "pro"] = "free"
    job_role: Literal["AI engineer", "sales", "other"] = "other"
    status: Literal["active", "non-active"] = "active"


# Schema untuk create (user baru)
class UserCreate(UserBase):
    password: str


class UpdateDetail(BaseModel):
    company_name: str
    job_role: Literal["AI engineer", "sales", "other"]
