from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IStorageAgentObj


@dataclass
class StoreAgentObjInput:
    agent_id: str
    agent_obj: dict


@dataclass
class StorageAgentObjOutput:
    agent_obj: dict


class StoreAgentObj(BaseUseCase[StoreAgentObjInput, StorageAgentObjOutput]):
    def __init__(self, storage_agent_obj: IStorageAgentObj):
        self.storage_agent_obj = storage_agent_obj

    async def execute(
        self, input_data: StoreAgentObjInput
    ) -> UseCaseResult[StorageAgentObjOutput]:
        try:
            store_agent = await self.storage_agent_obj.store_agent(
                input_data.agent_id, input_data.agent_obj
            )
            if not store_agent:
                return UseCaseResult.error_result(
                    "Store agent obj is failed",
                    RuntimeError("Store agent obj is failed"),
                )

            return UseCaseResult.success_result(
                StorageAgentObjOutput(input_data.agent_obj)
            )

        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while store agent obj: {str(e)}", e
            )
