from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class AuthBase(BaseModel):
    email: EmailStr


class AuthIn(AuthBase):
    password: str


class AuthOut(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]
