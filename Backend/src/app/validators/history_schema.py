from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class HistoryMetadataSchema(BaseModel):
    total_tokens: Optional[int] = None
    response_time: Optional[float] = None
    model: Optional[str] = None
    is_success: Optional[bool] = None


class HistoryMessageSchema(BaseModel):
    user_agent_id: str
    user_message: str
    response: str
    created_at: datetime
    metadata: Optional[HistoryMetadataSchema] = None


class HistoryStatsSchema(BaseModel):
    token_usage: int
    response_time: float
    messages: int


class HistoryDataSchema(BaseModel):
    history_message: List[HistoryMessageSchema]
    stats: HistoryStatsSchema


class HistoryResponse(BaseSchemaOut):
    data: HistoryDataSchema

