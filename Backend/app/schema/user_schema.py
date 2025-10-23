from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr

from app.schema.base import BaseSchemaOut


class BaseUserSchema(BaseModel):
    name: str
    email: EmailStr
    company_name: Optional[str] = "Tidak ada"
    plan: Literal["free", "normal", "pro"] = "free"
    job_role: Literal["AI engineer", "sales", "other"] = "other"
    status: Literal["active", "non-active"] = "active"


class DataUserSchema(BaseUserSchema):
    id: int
    role: Literal["admin", "user"]
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserPaginate(BaseModel):
    data_users: List[DataUserSchema]
    total: int
    page: int
    limit: int


class UserOutPaginate(BaseSchemaOut):
    data: UserPaginate
