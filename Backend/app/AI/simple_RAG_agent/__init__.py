import os
import time
from typing import Any, Dict, Optional

from fastapi import WebSocket
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.AI.simple_RAG_agent.workflow import Workflow
from app.dependencies.redis_storage import redis_storage
from app.dependencies.logger import get_logger

logger = get_logger(__name__)


class Agent:
    def __init__(
        self,
        base_prompt: str,
        tone: str,
        directory_path: str,
        chromadb_path: str,
        collection_name: str,
        model_llm: str,
        status: str = "active",
        include_memory=False,
        short_memory=False,
    ):
        self.status = status
        self.directory_path = directory_path
        self.llm_model = model_llm
        self.base_prompt = base_prompt
        self.tone = tone
        self.short_memory = short_memory
        # self.short_memory = short_memory
        self.workflow = Workflow(
            directory_path=directory_path,
            chromadb_path=chromadb_path,
            collection_name=collection_name,
            include_memory=include_memory,
            model_llm=self.llm_model,
            short_memory=self.short_memory,
            base_prompt=self.base_prompt,
            tone=self.tone,
        )
        self._history_messages = None
        self.response_time = None
        self.token_usage = None

    def execute(self, state: Dict, thread_id):
        start_time = time.perf_counter()
        result = self.workflow.run(state=state, thread_id=thread_id)
        end_time = time.perf_counter()
        self.response_time = round(end_time - start_time, 2)
        self.token_usage = result.get("total_token")
        self._history_messages = result["messages"]
        return result

    def add_document(self, file_name: str, file_type: str, document_id: str):
        """
        Add a document to the RAG system.

        Args:
            file_name: Name of the file to add
            file_type: Type of the file ('txt' or 'pdf')
            document_id: Unique identifier for the document

        Raises:
            HTTPException: If document loading or addition fails
        """
        try:
            # Ensure directory exists
            if not os.path.exists(self.directory_path + "/"):
                os.makedirs(self.directory_path, exist_ok=True)

            # Load document using RAG system
            documents = self.workflow.rag.load_single_document(
                self.directory_path, file_name, file_type
            )

            # Add documents to the RAG system
            self.workflow.rag.add_documents(documents, document_id)

            logger.info(
                f"Successfully added document '{file_name}' with ID '{document_id}'"
            )

        except Exception as e:
            logger.error(f"Failed to add document '{file_name}': {str(e)}")
            # Re-raise with more context
            raise Exception(
                f"Failed to add document '{file_name}' to RAG system: {str(e)}"
            ) from e

    def delete_document(self, document_id: str):
        """
        Delete a document from the RAG system.

        Args:
            document_id: Unique identifier of the document to delete

        Raises:
            Exception: If document deletion fails
        """
        try:
            self.workflow.rag.delete_document(document_id)
            logger.info(f"Successfully deleted document with ID '{document_id}'")
        except Exception as e:
            logger.error(f"Failed to delete document '{document_id}': {str(e)}")
            raise

    def update(self, data: Dict[str, Any]):
        """
        Update agent attributes. Allowed keys: base_prompt, status, model_llm, include_memory, short_memory, tone.
        """
        try:
            allowed_keys = {
                "base_prompt",
                "status",
                "model_llm",
                "include_memory",
                "short_memory",
                "tone",
            }
            for key, value in data.items():
                if key not in allowed_keys:
                    continue
                if key == "base_prompt":
                    self.base_prompt = value
                    self.workflow.base_prompt = value
                elif key == "status":
                    self.status = value
                elif key == "model_llm":
                    self.llm_model = value
                    self.workflow.model_llm = value
                elif key == "include_memory":
                    self.workflow.include_memory = value
                elif key == "short_memory":
                    self.short_memory = value
                    self.workflow.short_memory = value
                elif key == "tone":
                    self.tone = value
                    self.workflow.tone = value
            logger.info(f"Agent updated with: {data}")
        except Exception as e:
            logger.error(f"Error while update agent: {e}")
            raise

    def update_base_prompt(self, new_base_prompt: str):
        """Update the base prompt for the agent"""
        self.base_prompt = new_base_prompt
        self.workflow.base_prompt = new_base_prompt
        print(f"Base prompt updated to: {new_base_prompt}")

    def update_tone(self, new_tone: str):
        """Update the tone for the agent"""
        self.tone = new_tone
        self.workflow.tone = new_tone
        print(f"Tone updated to: {new_tone}")

    def update_short_memory(self, new_short_memory: bool):
        """Update the short memory setting for the agent"""
        self.short_memory = new_short_memory
        self.workflow.short_memory = new_short_memory
        print(f"Short memory updated to: {new_short_memory}")

    def pretty_print(self):
        if self._history_messages is None:
            print("No messages found.")
            return
        messages = ""
        print(self._history_messages)
        for message in self._history_messages:
            if isinstance(message, HumanMessage):
                msg = f"=========Human=========\n{message.content}\n\n"
            elif isinstance(message, AIMessage):
                if message.content == "":
                    msg = f"=========ToolCall=========\nTool Name: {message.tool_calls[0]['name']}\nparams: {message.tool_calls[0]['args']}\n\n"
                msg = f"=========AI=========\n{message.content}\n\n"
            elif isinstance(message, ToolMessage):
                msg = f"=========Tool Message=========\n{message.content}\n\n"
            else:
                continue
            messages += msg

        print(messages)
        return


if __name__ == "__main__":
    agent = Agent("docs", "data", "my_collections")
    # agent.add_document("peler.pdf", "pdf")
    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            print("bye bye")
            break
        agent.execute(
            {"user_message": user_input},
            "thread_123",
        )
#
