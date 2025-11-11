from typing import Literal, Optional

from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class CreateIntegrationSchema(BaseModel):
    platform: Literal["api", "telegram", "whatsapp"]
    status: Literal["active", "non-active"] = "active"
    api_key: Optional[str] = None


class CreateIntegrationResponse(BaseSchemaOut):
    data: CreateIntegrationSchema
