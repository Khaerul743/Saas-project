import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from src.core.utils.loop_manager import run_async
from src.infrastructure.redis.redis_storage import RedisStorage

from ....src.infrastructure.ai.agents.simple_rag_agent.models import AgentState
from ....src.infrastructure.ai.agents.simple_rag_agent.prompts import SimpleRagPrompt
from ....src.infrastructure.ai.components.tools import RetrieveDocumentTool

load_dotenv()


class Workflow:
    def __init__(
        self,
        directory_path: str,
        retrieve_document_tool: RetrieveDocumentTool,
        state_saver: RedisStorage,
        model_llm: str,
        base_prompt: str,
        tone: str,
        include_memory: bool = False,
        short_memory: bool = False,
    ):
        self.base_prompt = base_prompt
        self.tone = tone
        self.llm_for_reasoning = ChatOpenAI(model=model_llm)
        self.llm_for_explanation = ChatOpenAI(model="gpt-3.5-turbo")
        self.memory_provider = os.environ.get("MEMORY_PROVIDER")
        self.provider_host = os.environ.get("PROVIDER_HOST")
        self.provider_port = os.environ.get("PROVIDER_PORT")
        self.prompts = AgentPromptControl(
            is_include_memory=include_memory,
            memory_provider=self.memory_provider,
            provider_host=self.provider_host,
            provider_port=self.provider_port,
        )
        self.state_saver = RedisSaver(redis_url=state_saver.redis_url)
        self.short_memory = short_memory
        self.retreive_document_tool = retrieve_document_tool
        self.build: CompiledStateGraph[AgentState, None, AgentState, AgentState] = (
            self._build_workflow()
        )
        self.directiory_path = directory_path

    def _build_workflow(self):
        graph = StateGraph(AgentState)
        graph.add_node("main_agent", self._main_agent)
        graph.add_node(
            "read_document", ToolNode(tools=[self.retreive_document_tool.read_document])
        )
        graph.add_node("answer_rag_question", self._agent_answer_rag_question)
        graph.add_edge(START, "main_agent")
        graph.add_conditional_edges(
            "main_agent",
            self._should_continue,
            {"tool_call": "read_document", "end": END},
        )
        graph.add_edge("read_document", "answer_rag_question")
        graph.add_edge("answer_rag_question", END)

        return graph.compile(checkpointer=self.state_saver)

    # def _checking_message_type(self, state: AgentState):
    #     if state.is_include_document and os.path.exists(
    #         f"{self.directiory_path}/{state.document_name}"
    #     ):
    #         return "describe_document"
    #     return "main_agent"

    def _formatted_message(self, messages):
        formatted = []
        for message in messages:
            data = {}
            if isinstance(message, HumanMessage):
                data["role"] = "user"
                data["content"] = message.content
                formatted.append(data)
            elif isinstance(message, AIMessage):
                data["role"] = "assistant"
                data["content"] = message.content
                formatted.append(data)
        return formatted

    def _send_ws_message(
        self, include_ws: bool, message: Dict[str, Any], user_id: Optional[str] = None
    ):
        if include_ws:
            if user_id:
                run_async(
                    ws_manager.send_to_user(f"invoke_agent_{user_id}", message=message)
                )

    def _main_agent(self, state: AgentState) -> Dict[str, Any]:
        prompt = self.prompts.main_agent(
            state.user_message, self.base_prompt, self.tone
        )
        all_previous_messages = []
        if self.short_memory:
            all_previous_messages = state.messages
        messages = [prompt[0]] + all_previous_messages + [prompt[1]]
        # print(messages)
        llm = self.llm_for_reasoning.bind_tools(
            [self.retreive_document_tool.read_document]
        )
        response = llm.invoke(messages)
        if self.prompts.is_include_memory:
            message = [
                HumanMessage(content=state.user_message),
                AIMessage(content=response.content),
            ]
            formatted_message = self._formatted_message(message)
            print(formatted_message)
            self.prompts.memory.add_context(formatted_message, self.prompts.memory_id)
        total_tokens = response.usage_metadata["total_tokens"]

        # print(f"AI: {response.content}")
        self._send_ws_message(
            state.include_ws,
            {
                "type": "reasoning",
                "message": "Agent is reasoning...",
            },
            state.user_id,
        )

        return {
            "messages": state.messages
            + [HumanMessage(content=state.user_message)]
            + [response],
            "response": response.content,
            "total_token": state.total_token + total_tokens,
        }

    def _should_continue(self, state: AgentState):
        last_message = state.messages[-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            self._send_ws_message(
                state.include_ws,
                {
                    "type": "reasoning",
                    "message": "Agent using the tool...",
                },
                state.user_id,
            )
            return "tool_call"
        return "end"

    def _agent_answer_rag_question(self, state: AgentState):
        tool_message = state.messages[-1].content
        prompt = self.prompts.agent_answer_rag_question(
            state.user_message, tool_message
        )
        llm = self.llm_for_explanation
        response = llm.invoke([prompt[0]] + state.messages + [prompt[1]])
        total_tokens = response.usage_metadata["total_tokens"]
        # print(f"response: {response.content}")
        return {
            "messages": state.messages + [response],
            "response": response.content,
            "total_token": state.total_token + total_tokens,
        }

    def run(self, state: Dict, thread_id: str):
        return self.build.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )


# if __name__ == "__main__":
#     agent = Workflow("docs", "data", "my_collections")

#     while True:
#         user_input = input("Human: ")
#         if user_input == "exit":
#             print("bye bye")
#             break
#         result = agent.run(state={"user_message": user_input}, thread_id="thread_123")
#     print(result)
