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


# Schema untuk update (optional fields)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    company_name: Optional[str] = None
    # plan: Optional[Literal["free", "normal", "pro"]] = None
    job_role: Optional[Literal["AI engineer", "sales", "other"]] = None
    # status: Optional[Literal["active", "non-active"]] = None
    # password: Optional[str] = None


# Schema untuk response (ke client, tanpa password)
class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True  # penting untuk baca dari SQLAlchemy object


class UserResponseAPI(BaseModel):
    status: str
    message: str
    data: UserOut


class UpdateDetail(BaseModel):
    company_name: str
    job_role: Literal["AI engineer", "sales", "other"]
