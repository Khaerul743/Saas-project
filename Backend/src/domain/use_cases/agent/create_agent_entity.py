import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.core.utils.agent_utils import generate_agent_id
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IAgentRepository


@dataclass
class CreateAgentEntityInput:
    user_id: int
    agent_data: dict


@dataclass
class CreateAgentEntityOutput:
    id: str
    user_id: int
    name: str
    model: str
    role: str
    description: str
    status: str
    base_prompt: str
    short_term_memory: bool
    long_term_memory: bool
    tone: str
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None


class CreateAgentEntity(BaseUseCase[CreateAgentEntityInput, CreateAgentEntityOutput]):
    def __init__(self, agent_repository: IAgentRepository):
        self.agent_repository = agent_repository

    async def execute(
        self, input_data: CreateAgentEntityInput
    ) -> UseCaseResult[CreateAgentEntityOutput]:
        try:
            agent_id = generate_agent_id()

            while True:
                agent = await self.agent_repository.get_agent_by_id(agent_id)
                if agent:
                    agent_id = generate_agent_id()
                else:
                    break
                time.sleep(0.001)
            # Ensure agent_data is a dict and add agent_id
            if not isinstance(input_data.agent_data, dict):
                agent_data = dict(input_data.agent_data) if hasattr(input_data.agent_data, '__iter__') else {}
            else:
                agent_data = input_data.agent_data.copy()
            
            agent_data["id"] = agent_id
            # Call with positional arguments only - no unpacking
            agent_entity = await self.agent_repository.create_agent(
                input_data.user_id, agent_data
            )
            return UseCaseResult.success_result(
                CreateAgentEntityOutput(
                    id=agent_entity.id,
                    user_id=agent_entity.user_id,
                    name=agent_entity.name,
                    model=agent_entity.model,
                    description=agent_entity.description,
                    status=agent_entity.status,
                    base_prompt=agent_entity.base_prompt,
                    avatar=agent_entity.avatar,
                    created_at=agent_entity.created_at,
                    short_term_memory=agent_entity.short_term_memory,
                    long_term_memory=agent_entity.long_term_memory,
                    tone=agent_entity.tone,
                    role=agent_entity.role,
                )
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while create agent entity: {str(e)}", e
            )
