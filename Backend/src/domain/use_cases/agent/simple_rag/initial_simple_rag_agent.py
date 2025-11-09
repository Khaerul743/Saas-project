from dataclasses import dataclass
from typing import Literal, Optional

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.ai.agents import SimpleRagAgent

from ..store_agent_in_memory import StoreAgentInMemory, StoreAgentInMemoryInput


@dataclass
class InitialSimpleRagAgentInput:
    agent_id: str
    chromadb_path: str
    collection_name: str
    llm_provider: str
    llm_model: str
    tone: Literal["friendly", "formal", "casual", "profesional"]
    base_prompt: Optional[str] = None
    include_short_memory: bool = False
    include_long_memory: bool = False


@dataclass
class InitialSimpleRagAgentOutput:
    agent: SimpleRagAgent


class InitialSimpleRagAgent(
    BaseUseCase[InitialSimpleRagAgentInput, InitialSimpleRagAgentOutput]
):
    def __init__(self, store_agent_in_memory: StoreAgentInMemory):
        self.store_agent_in_memory = store_agent_in_memory

    def execute(
        self, input_data: InitialSimpleRagAgentInput
    ) -> UseCaseResult[InitialSimpleRagAgentOutput]:
        try:
            # Initial simple rag agent
            simple_rag_agent = SimpleRagAgent(
                input_data.chromadb_path,
                input_data.collection_name,
                input_data.llm_provider,
                input_data.llm_model,
                input_data.tone,
                input_data.base_prompt,
                input_data.include_short_memory,
                input_data.include_long_memory,
            )

            # save the agent in memory
            store_agent = self.store_agent_in_memory.execute(
                StoreAgentInMemoryInput(input_data.agent_id, simple_rag_agent)
            )

            if not store_agent.is_success():
                return self._return_exception(store_agent)

            return UseCaseResult.success_result(
                InitialSimpleRagAgentOutput(simple_rag_agent)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while initial simple rag agent: {str(e)}", e
            )
