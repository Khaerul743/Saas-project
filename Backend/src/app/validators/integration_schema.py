from typing import Literal, Optional

from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class CreateIntegrationSchema(BaseModel):
    platform: Literal["api", "telegram", "whatsapp"]
    status: Literal["active", "non-active"] = "active"
    api_key: Optional[str] = None


class CreateIntegrationResponse(BaseSchemaOut):
    data: CreateIntegrationSchema


class DeleteIntegrationSchema(BaseModel):
    platform: Literal["api", "telegram", "whatsapp"]


class DeleteIntegrationResult(BaseModel):
    success: bool


class DeleteIntegrationResponse(BaseSchemaOut):
    data: DeleteIntegrationResult


class IntegrationItemSchema(BaseModel):
    id: int
    agent_id: str
    platform: Literal["api", "telegram", "whatsapp"]
    status: Literal["active", "non-active"]
    api_key: Optional[str] = None
    created_at: str


class GetAllIntegrationData(BaseModel):
    integrations: list[IntegrationItemSchema]


class GetAllIntegrationResponse(BaseSchemaOut):
    data: GetAllIntegrationData