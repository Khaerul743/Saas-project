from dataclasses import dataclass
from typing import Any, Dict, Literal

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.ai.agents import BaseAgent

from .simple_rag.initial_simple_rag_agent import (
    InitialSimpleRagAgent,
    InitialSimpleRagAgentInput,
)


@dataclass
class InitialAgentAgainInput:
    agent_id: str
    role: Literal["simple RAG agent"]
    agent_obj: Dict[str, Any]


@dataclass
class InitialAgentAgainOutput:
    agent: BaseAgent


class InitialAgentAgain(BaseUseCase[InitialAgentAgainInput, InitialAgentAgainOutput]):
    def __init__(self, initial_simple_rag_agent: InitialSimpleRagAgent):
        self.initial_simple_rag_agent = initial_simple_rag_agent

    def execute(
        self, input_data: InitialAgentAgainInput
    ) -> UseCaseResult[InitialAgentAgainOutput]:
        try:
            agent = None
            if input_data.role == "simple RAG agent":
                initial_agent = self.initial_simple_rag_agent.execute(
                    InitialSimpleRagAgentInput(
                        input_data.agent_id,
                        input_data.agent_obj.get("chromadb_path"),
                        input_data.agent_obj.get("collection_name"),
                        input_data.agent_obj.get("llm_provider"),
                        input_data.agent_obj.get("model_llm"),
                        input_data.agent_obj.get("tone"),
                        input_data.agent_obj.get("base_prompt"),
                        input_data.agent_obj.get("short_memory"),
                        input_data.agent_obj.get("long_memory"),
                    )
                )

                if not initial_agent.is_success():
                    return self._return_exception(initial_agent)

                get_agent = initial_agent.get_data()
                if not get_agent:
                    return UseCaseResult.error_result(
                        "Agent is empty", RuntimeError("Agent is empty")
                    )

                agent = get_agent.agent

            if not agent:
                return UseCaseResult.error_result(
                    "Role agent is not available",
                    ValueError("Role agent is not available"),
                )

            return UseCaseResult.success_result(InitialAgentAgainOutput(agent))
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while initial agent again: {str(e)}", e
            )
