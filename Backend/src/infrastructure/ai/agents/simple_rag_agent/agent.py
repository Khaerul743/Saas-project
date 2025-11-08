from typing import Literal, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver

from src.infrastructure.redis.redis_storage import RedisStorage

from ...components.tools import RetrieveDocumentTool
from .. import BaseAgent
from .prompts import SimpleRagPrompt
from .workflow import SimpleRagWorkflow


class SimpleRagAgent(BaseAgent):
    def __init__(
        self,
        chromadb_path: str,
        collection_name: str,
        llm_provider,
        llm_model: str,
        tone: Literal["friendly", "formal", "casual", "profesional"],
        base_prompt: Optional[str] = None,
        include_short_memory: bool = False,
        include_long_memory: bool = False,
    ):
        self.retrieve_document_tool = RetrieveDocumentTool(
            chromadb_path, collection_name
        )
        # self.state_saver = RedisStorage()
        # self.checkpoint = RedisSaver(redis_url=self.state_saver.redis_url)
        self.checkpoint = MemorySaver()
        self.prompts = SimpleRagPrompt(tone, base_prompt)
        super().__init__(
            SimpleRagWorkflow(
                self.retrieve_document_tool,
                self.checkpoint,
                self.prompts,
                llm_provider,
                llm_model,
                include_short_memory,
                include_long_memory,
            )
        )
