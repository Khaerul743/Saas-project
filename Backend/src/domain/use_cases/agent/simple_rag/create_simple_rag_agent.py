from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile

from ...base import BaseUseCase, UseCaseResult
from ..create_agent_entity import (
    CreateAgentEntity,
    CreateAgentEntityInput,
    CreateAgentEntityOutput,
)
from ..document.store_to_chroma import AddDocumentToAgent, AddDocumentToAgentInput
from ..document.uploaded_document import (
    UploadedDocumentHandler,
    UploadedDocumentInput,
)
from ..store_agent_obj import StoreAgentObj, StoreAgentObjInput
from .initial_simple_rag_agent import (
    InitialSimpleRagAgent,
    InitialSimpleRagAgentInput,
)


@dataclass
class CreateSimpleRagAgentInput:
    user_id: int
    llm_provider: str
    agent_data: dict
    chroma_db_path: str
    file: Optional[UploadFile] = None


class CreateSimpleRagAgent(
    BaseUseCase[CreateSimpleRagAgentInput, CreateAgentEntityOutput]
):
    def __init__(
        self,
        uploaded_document_handler: UploadedDocumentHandler,
        document_store: AddDocumentToAgent,
        create_agent_entity: CreateAgentEntity,
        store_agent_obj: StoreAgentObj,
        initial_simple_rag_agent: InitialSimpleRagAgent,
    ):
        self.uploaded_document_handler = uploaded_document_handler
        self.document_store = document_store
        self.create_agent_entity = create_agent_entity
        self.store_agent_obj = store_agent_obj
        self.initial_simple_rag_agent = initial_simple_rag_agent

    async def execute(
        self, input_data: CreateSimpleRagAgentInput
    ) -> UseCaseResult[CreateAgentEntityOutput]:
        try:
            # Add data agent to database
            add_agent = await self.create_agent_entity.execute(
                CreateAgentEntityInput(input_data.user_id, input_data.agent_data)
            )
            if not add_agent.is_success():
                return self._return_exception(add_agent)

            get_data_agent = add_agent.get_data()
            if not get_data_agent:
                return UseCaseResult.error_result(
                    "The agent data is empty",
                    RuntimeError("The agent data is empty"),
                )

            agent_id = get_data_agent.id
            # Save document
            collection_name = None
            directory_path = None
            if input_data.file:
                document_process = await self.uploaded_document_handler.execute(
                    UploadedDocumentInput(input_data.user_id, agent_id, input_data.file)
                )
                if not document_process.is_success():
                    return self._return_exception(document_process)

                document_result_data = document_process.get_data()
                if not document_result_data:
                    return UseCaseResult.error_result(
                        "The document result is empty",
                        RuntimeError("The document result is empty"),
                    )
                directory_path = document_result_data.directory_path
                # Store document to chroma db vectorstore
                add_to_chroma_db = self.document_store.execute(
                    AddDocumentToAgentInput(agent_id, document_result_data)
                )
                if not add_to_chroma_db.is_success():
                    return self._return_exception(add_to_chroma_db)

                get_data_collection_name = add_to_chroma_db.get_data()
                if not get_data_collection_name:
                    return UseCaseResult.error_result(
                        "Collection name is empty",
                        RuntimeError("Collection name empty"),
                    )

                collection_name = get_data_collection_name.collection_name

            # Store agent obj
            agent_obj = {
                "base_prompt": get_data_agent.base_prompt,
                "tone": get_data_agent.tone,
                "directory_path": directory_path,
                "chromadb_path": input_data.chroma_db_path,
                "collection_name": collection_name,
                "llm_provider": input_data.llm_provider,
                "model_llm": get_data_agent.model,
                "short_memory": get_data_agent.short_term_memory,
                "long_memory": get_data_agent.long_term_memory,
                "role": "simple RAG agent",
            }
            store_agent_obj_result = await self.store_agent_obj.execute(
                StoreAgentObjInput(agent_id, agent_obj)
            )

            if not store_agent_obj_result.is_success():
                return self._return_exception(store_agent_obj_result)

            # Initial simple rag agent
            self.initial_simple_rag_agent.execute(
                InitialSimpleRagAgentInput(
                    agent_id,
                    input_data.chroma_db_path,
                    collection_name or "default",
                    input_data.llm_provider,
                    get_data_agent.model,
                    get_data_agent.tone,
                    get_data_agent.base_prompt,
                    get_data_agent.short_term_memory,
                    get_data_agent.long_term_memory,
                )
            )

            return UseCaseResult.success_result(get_data_agent)
        except Exception as e:
            self.uploaded_document_handler.save_file.cleanup_file_on_error(
                directory_path
            )
            return UseCaseResult.error_result(
                f"unexpected error while create simple rag agent: {str(e)}", e
            )

    def _return_exception(self, process: UseCaseResult):
        get_exception = process.get_exception()
        get_error_message = process.get_error()
        return UseCaseResult.error_result(get_error_message or "", get_exception)
