from abc import ABC, abstractmethod
from typing import Any, Dict


class IStorageAgentObj(ABC):
    @abstractmethod
    async def store_agent(self, agent_id: str, agent_obj: Dict[str, Any]) -> bool:
        pass
