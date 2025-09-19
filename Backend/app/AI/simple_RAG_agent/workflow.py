import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from app.AI.document_store.RAG import RAGSystem
from app.AI.simple_RAG_agent.models import AgentState
from app.AI.simple_RAG_agent.prompts import AgentPromptControl
from app.AI.simple_RAG_agent.tools import AgentTools

load_dotenv()


class Workflow:
    def __init__(
        self,
        directory_path: str,
        chromadb_path: str,
        collection_name: str,
        model_llm: str,
        base_prompt: str,
        tone: str,
        include_memory: bool = False,
        short_memory: bool = False,
    ):
        self.base_prompt = base_prompt
        self.tone = tone
        self.chromadb_path = chromadb_path
        self.collection_name = collection_name
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
        self.memory = MemorySaver()
        self.short_memory = short_memory
        self.tools = AgentTools(self.chromadb_path, self.collection_name)
        self.build = self._build_workflow()
        self.rag = RAGSystem(self.chromadb_path, self.collection_name)
        self.directiory_path = directory_path

    def _build_workflow(self):
        graph = StateGraph(AgentState)
        graph.add_node("main_agent", self._main_agent)
        graph.add_node("get_document", ToolNode(tools=[self.tools.get_document]))
        graph.add_node("answer_rag_question", self._agent_answer_rag_question)
        # graph.add_node("load_document", self._load_document)
        # graph.add_node("describe_document", self._agent_describe_document)

        # graph.add_conditional_edges(
        #     START,
        #     self._checking_message_type,
        #     {"describe_document": "load_document", "main_agent": "main_agent"},
        # )
        # graph.add_edge("load_document", "describe_document")
        # graph.add_edge("describe_document", END)

        graph.add_edge(START, "main_agent")
        graph.add_conditional_edges(
            "main_agent",
            self._should_continue,
            {"tool_call": "get_document", "end": END},
        )
        graph.add_edge("get_document", "answer_rag_question")
        graph.add_edge("answer_rag_question", END)

        return graph.compile(checkpointer=self.memory)

    def _checking_message_type(self, state: AgentState):
        if state.is_include_document and os.path.exists(
            f"{self.directiory_path}/{state.document_name}"
        ):
            return "describe_document"
        return "main_agent"

    # def _load_document(self, state: AgentState):
    #     if not os.path.exists(self.directiory_path + "/"):
    #         os.makedirs(self.directiory_path, exist_ok=True)
    #     documents = self.rag.load_document(self.directiory_path)
    #     self.rag.add_document(documents=documents)

    #     get_single_docs = self.rag.load_one_document(
    #         self.directiory_path, state.document_name, state.document_type
    #     )
    #     document = "".join([item.page_content for item in get_single_docs])

    #     if not os.path.exists(f"{self.directiory_path}/{state.document_name}"):
    #         document = "not found."

    #     return {"document_content": document}

    # def _agent_describe_document(self, state: AgentState):
    #     prompt = self.prompts.agent_describe_document(
    #         state.user_message, state.document_content
    #     )
    #     llm = self.llm_for_explanation
    #     response = llm.invoke(prompt)
    #     return {
    #         "messages": state.messages + [response],
    #         "response": response.content,
    #         "is_include_document": False,
    #     }

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

    def _main_agent(self, state: AgentState) -> Dict[str, Any]:
        prompt = self.prompts.main_agent(state.user_message, self.base_prompt, self.tone)
        print(f"prompt: {prompt}")
        all_previous_messages = []
        if self.short_memory:
            all_previous_messages = state.messages
        messages = [prompt[0]] + all_previous_messages + [prompt[1]]
        # print(messages)
        llm = self.llm_for_reasoning.bind_tools([self.tools.get_document])
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
        print(f"state: {state.messages} ")
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


if __name__ == "__main__":
    agent = Workflow("docs", "data", "my_collections")

    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            print("bye bye")
            break
        result = agent.run(state={"user_message": user_input}, thread_id="thread_123")
    print(result)
