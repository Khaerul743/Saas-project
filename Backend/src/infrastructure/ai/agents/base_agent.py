import time
from typing import Any, Dict

from .base_model import BaseAgentStateModel
from .base_workflow import BaseWorkflow


class BaseAgent:
    def __init__(self, workflow: BaseWorkflow):
        self.workflow = workflow
        self._response_time = 0
        self._result = None

    def get_response_time(self):
        return self._response_time

    def get_token_usage(self):
        return self.workflow.get_total_token()

    def get_llm_model(self):
        return self.workflow.llm_model

    def execute(self, state: BaseAgentStateModel, thread_id) -> Dict[str, Any] | Any:
        start_time = time.perf_counter()
        result = self.workflow.run(state, thread_id)
        self._result = result
        end_time = time.perf_counter()
        self._response_time = round(end_time - start_time, 2)
        return result

    def get_response(self):
        if self._result is None:
            return None

        return self._result.get("response")
