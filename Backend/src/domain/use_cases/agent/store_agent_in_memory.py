from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.infrastructure.ai.agents import BaseAgent
from src.infrastructure.data import AgentManager


@dataclass
class StoreAgentInMemoryInput:
    agent_id: str
    agent: BaseAgent


@dataclass
class StoreAgentInMemoryOutput:
    agent_id: str


class StoreAgentInMemory(
    BaseUseCase[StoreAgentInMemoryInput, StoreAgentInMemoryOutput]
):
    def __init__(self, agent_obj_manager: AgentManager):
        self.agent_obj_manager = agent_obj_manager

    def execute(
        self, input_data: StoreAgentInMemoryInput
    ) -> UseCaseResult[StoreAgentInMemoryOutput]:
        try:
            self.agent_obj_manager.store_agent_in_memory(
                input_data.agent_id, input_data.agent
            )
            return UseCaseResult.success_result(
                StoreAgentInMemoryOutput(agent_id=input_data.agent_id)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while store the agent in memory: {str(e)}", e
            )
