from pydantic import BaseModel


class BaseSchemaOut(BaseModel):
    status: str
    message: str


class BasePaginateOut(BaseModel):
    total: int
    page: int
    limit: int
