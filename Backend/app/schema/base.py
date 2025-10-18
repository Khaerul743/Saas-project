from pydantic import BaseModel


class BaseSchemaOut(BaseModel):
    status: str
    message: str
