from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel


class IntegrationBase(BaseModel):
    platform: Literal["whatsapp", "telegram", "api"]
    status: Literal["active", "non-active"] = "active"


class CreateIntegration(IntegrationBase):
    api_key: Optional[str] = None

class UpdateIntegration(BaseModel):
    platform: Literal["whatsapp", "telegram", "api"]
    api_key: str
    
class IntegrationOut(IntegrationBase):
    agent_id: int
    created_at: datetime
