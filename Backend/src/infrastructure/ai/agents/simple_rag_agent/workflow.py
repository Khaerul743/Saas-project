from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from ...components.tools import RetrieveDocumentTool
from ..base_workflow import BaseWorkflow
from .models import SimpleRagState
from .prompts import SimpleRagPrompt

load_dotenv()


class SimpleRagWorkflow(BaseWorkflow):
    def __init__(
        self,
        retrieve_document_tool: RetrieveDocumentTool,
        state_saver: BaseCheckpointSaver,
        prompt: SimpleRagPrompt,
        llm_provider: str = "openai",
        llm_model: str = "gpt-3.5-turbo",
        include_short_memory: bool = False,
        include_long_memory: bool = False,
    ):
        super().__init__(
            llm_model, llm_provider, include_long_memory, include_short_memory
        )
        self.retrieve_document_tool = retrieve_document_tool
        # Use MemorySaver for now since RedisSaver has async issues
        # Can be replaced with RedisSaver when async support is fully implemented
        # self.checkpointer = MemorySaver() if state_saver is None else MemorySaver()
        self.checkpointer = state_saver
        self.prompts = prompt
        self.build = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(SimpleRagState)
        graph.add_node("main_agent", self._main_agent)
        graph.add_node(
            "read_document", ToolNode(tools=[self.retrieve_document_tool.read_document])
        )
        graph.add_node("answer_by_rag", self._answer_by_rag)
        graph.add_edge(START, "main_agent")
        graph.add_conditional_edges(
            "main_agent",
            self.conditional_tool_call,
            {"tool_call": "read_document", "end": END},
        )

        graph.add_edge("read_document", "answer_by_rag")
        graph.add_edge("answer_by_rag", END)

        return graph.compile(checkpointer=self.checkpointer)

    def _main_agent(self, state: SimpleRagState) -> Dict[str, Any]:
        prompt = self.prompts.main_agent(state.user_message)
        all_previous_messages = self.get_all_previous_messages(state.messages)
        messages: list[Any] = [prompt[0]] + list(all_previous_messages) + [prompt[1]]

        response = self.call_llm_with_tool(
            messages, [self.retrieve_document_tool.read_document]
        )

        # response = self.call_llm(messages)
        if self.is_include_long_memory():
            message = [
                HumanMessage(content=state.user_message),
                AIMessage(content=response.content),
            ]

            self.memory.add_context(message)

        self.estimate_total_tokens(prompt, state.user_message, response.content)

        return {
            "messages": list(state.messages)
            + [HumanMessage(content=state.user_message)]
            + [response],
            "response": response.content,
        }

    def _answer_by_rag(self, state: SimpleRagState):
        tool_message = self.get_content_state_last_message(state.messages)
        print(f"TOOL MESSAGE: {tool_message}")
        # llm prompt
        prompt = self.prompts.agent_answer_rag_question(
            state.user_message, tool_message
        )
        all_previous_messages = self.get_all_previous_messages(state.messages)
        messages: list[Any] = [prompt[0]] + list(all_previous_messages) + [prompt[1]]
        response = self.call_llm(messages)

        return {
            "messages": list(state.messages) + [response],
            "response": response.content,
        }

    def run(self, state: SimpleRagState, thread_id: str):
        return self.build.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )
