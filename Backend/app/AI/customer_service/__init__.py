import os
import time
from typing import Any, Dict, List, Optional

from fastapi import WebSocket
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.AI.customer_service.tools import AgentTools
from app.AI.customer_service.workflow import Workflow
from app.AI.document_store.RAG import RAGSystem
from app.models.company_information.company_model import CreateCompanyInformation
from app.dependencies.logger import get_logger

logger = get_logger(__name__)


class Agent:
    def __init__(
        self,
        base_prompt: str,
        tone: str,
        llm_model: str,
        directory_path: str,
        chromadb_path: str,
        collection_name: str,
        available_databases: List[str],
        detail_data: str,
        company_information: CreateCompanyInformation,
        long_memory: bool = False,
        short_memory: bool = False,
        status: str = "active",
        **kwargs,
    ):
        self.status = status
        self.directory_path = directory_path
        self.tools = AgentTools(
            chromadb_path=chromadb_path, collection_name=collection_name
        )
        self.company_information: CreateCompanyInformation = company_information
        self.llm_model = llm_model
        self.rag = RAGSystem(
            chroma_directiory=chromadb_path, collection_name=collection_name
        )
        self.workflow = Workflow(
            base_prompt=base_prompt,
            tone=tone,
            tools=self.tools,
            available_databases=available_databases,
            detail_data=detail_data,
            company_information=self.company_information,
            directory_path=directory_path,  # ✅ Pass directory_path to workflow
            short_memory=short_memory,
            long_memory=long_memory,
            **kwargs,
        )
        self._history_messages = None
        self.response_time = 0.0
        self.token_usage = 0

    def execute(self, state: Dict, thread_id):
        start_time = time.perf_counter()
        result = self.workflow.run(state=state, thread_id=thread_id)
        end_time = time.perf_counter()
        self.response_time = round(end_time - start_time, 2)
        self.token_usage = result.get("total_token")
        self._history_messages = result["messages"]
        return result

    def add_document(self, file_name: str, file_type: str, document_id: str):
        try:
            # Ensure directory exists
            if not os.path.exists(self.directory_path + "/"):
                os.makedirs(self.directory_path, exist_ok=True)

            documents = self.rag.load_single_document(
                self.directory_path, file_name, file_type
            )
            logger.info(f"Successfully loaded document: {file_name}")
            self.rag.add_documents(documents, document_id)
            logger.info(
                f"Successfully added document '{file_name}' with ID '{document_id}'"
            )
        except Exception as e:
            logger.error(f"Failed to add document '{file_name}': {str(e)}")
            raise Exception(
                f"Failed to add document '{file_name}' to RAG system: {str(e)}"
            ) from e

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
            company_keys = {
                "company_name",
                "industry",
                "company_description",
                "address",
                "email",
                "website",
                "fallback_email",
            }

            for key, value in data.items():
                if key not in allowed_keys:
                    continue
                if key == "base_prompt":
                    self.base_prompt = value
                    self.workflow.base_prompt = value
                elif key == "status":
                    self.status = value
                # elif key == "model_llm":
                #     self.llm_model = value
                #     self.workflow.model_llm = value
                elif key == "include_memory":
                    self.workflow.include_memory = value
                elif key == "short_memory":
                    self.short_memory = value
                    self.workflow.short_memory = value
                elif key == "tone":
                    self.tone = value
                    self.workflow.tone = value
                elif key in company_keys:
                    if key == "company_name":
                        key = "name"
                    elif key == "company_description":
                        key = "description"
                    setattr(self.company_information, key, value)
                    setattr(self.workflow.company_information, key, value)

            logger.info(f"Agent updated with: {data}")
        except Exception as e:
            logger.error(f"Error while update agent: {e}")
            raise

    def delete_document(self, document_id: str):
        try:
            self.rag.delete_document(document_id)
            logger.info(f"Successfully deleted document with ID '{document_id}'")
        except Exception as e:
            logger.error(f"Failed to delete document '{document_id}': {str(e)}")
            raise

    def get_token_usage(self):
        return self.token_usage

    def get_response_time(self):
        return self.response_time

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
