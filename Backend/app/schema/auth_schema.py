from pydantic import BaseModel, EmailStr

from app.schema.base import BaseSchemaOut


class AuthBase(BaseModel):
    email: EmailStr


class RegisterIn(AuthBase):
    name: str
    password: str


class LoginIn(AuthBase):
    password: str


class AuthOutData(AuthBase):
    name: str


class AuthOut(BaseSchemaOut):
    data: AuthOutData
