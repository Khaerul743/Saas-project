from typing import Annotated, Any, Optional, Sequence

from .. import BaseAgentStateModel


class SimpleRagState(BaseAgentStateModel):
    is_include_document: bool = False
    document_name: Optional[str] = "none"
    document_content: Optional[str] = "none"
    document_type: Optional[str] = "none"
    # can_answer: bool = False
    reason: Optional[str] = "none"
    include_ws: bool = False
    user_id: Optional[str] = None
