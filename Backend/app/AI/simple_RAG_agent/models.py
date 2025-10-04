from typing import Annotated, Any, Optional, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from fastapi import WebSocket


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_message: Optional[str] = "none"
    response: Optional[str] = "none"
    is_include_document: bool = False
    document_name: Optional[str] = "none"
    document_content: Optional[str] = "none"
    document_type: Optional[str] = "none"
    total_token: Optional[int] = 0
    # can_answer: bool = False
    reason: Optional[str] = "none"
    websocket: bool = False