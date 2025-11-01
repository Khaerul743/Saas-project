from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr

from src.app.validators.base import BasePaginateOut, BaseSchemaOut


class BaseUserSchema(BaseModel):
    name: str
    email: EmailStr
    company_name: Optional[str] = "Tidak ada"
    plan: Literal["free", "normal", "pro"] = "free"
    job_role: Literal["AI engineer", "sales", "other"] = "other"


class DataUserSchema(BaseUserSchema):
    id: int
    role: Literal["admin", "user"]
    created_at: datetime
    status: Literal["active", "non-active"] = "active"
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserPaginate(BasePaginateOut):
    data_users: List[DataUserSchema]


class UserOutPaginate(BaseSchemaOut):
    data: UserPaginate


class ShowUserProfile(BaseUserSchema):
    id: int


class ShowUserProfileOut(BaseSchemaOut):
    data: ShowUserProfile


# Schema untuk update user (optional fields)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    job_role: Optional[Literal["AI engineer", "sales", "other"]] = None


class UserUpdateOut(BaseSchemaOut):
    data: UserUpdate


# Schema untuk response (ke client, tanpa password)
class UserOut(BaseUserSchema):
    id: int
    role: Literal["admin", "user"]
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    status: Literal["active", "non-active"] = "active"

    class Config:
        orm_mode = True  # penting untuk baca dari SQLAlchemy object


# Schema untuk update user plan
class UpdateUserPlan(BaseModel):
    plan: Literal["free", "normal", "pro"]


class UpdateUserPlanOut(UpdateUserPlan):
    email: EmailStr


class UpdateUserPlanResponse(BaseSchemaOut):
    data: UpdateUserPlanOut


# Schema untuk response API
class UserResponseAPI(BaseSchemaOut):
    data: UserOut
