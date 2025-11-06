import time

from .base_model import BaseAgentStateModel
from .base_workflow import BaseWorkflow


class BaseAgent:
    def __init__(self, workflow: BaseWorkflow):
        self.workflow = workflow
        self._response_time = 0

    def get_response_time(self):
        return self._response_time

    def get_token_usage(self):
        return self.workflow.get_total_token()

    def execute(self, state: BaseAgentStateModel, thread_id):
        start_time = time.perf_counter()
        result = self.workflow.run(state, thread_id)
        end_time = time.perf_counter()
        self._response_time = round(end_time - start_time, 2)
        return result
