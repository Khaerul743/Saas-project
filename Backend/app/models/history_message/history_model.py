from datetime import datetime
from typing import Dict, Literal, Optional

from pydantic import BaseModel


class HistoryBase(BaseModel):
    user_message: str
    response: str
    created_at: datetime


class HistoryOut(HistoryBase):
    user_agent_id: int
