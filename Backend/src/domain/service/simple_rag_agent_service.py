from typing import Optional

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.validators.agent_schema import CreateAgent
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.core.utils.save_file import SaveFileHandler
from src.domain.repositories import AgentRepository, DocumentRepository
from src.domain.service import BaseService
from src.domain.use_cases.agent import (
    AddDocumentToAgent,
    CreateAgentEntity,
    CreateSimpleRagAgent,
    CreateSimpleRagAgentInput,
    InitialSimpleRagAgent,
    StoreAgentInMemory,
    StoreAgentObj,
    UploadedDocumentHandler,
)
from src.infrastructure.data import AgentManager, agent_manager
from src.infrastructure.redis.redis_storage import RedisStorage


class SimpleRagAgentService(BaseService):
    def __init__(self, db: AsyncSession, request=None):
        super().__init__(__name__, request)
        self.db = db
        self.storage_agent_obj = RedisStorage()
        self.chroma_db_path = "chroma_db"
        self.document_repository = DocumentRepository(db)
        self.agent_repository = AgentRepository(db)
        self.agent_manager = agent_manager
        self.save_file = SaveFileHandler()
        self.uploaded_document_handler = UploadedDocumentHandler(
            self.document_repository, self.save_file
        )
        self.add_document_to_agent = AddDocumentToAgent(self.chroma_db_path)
        self.create_agent_entity = CreateAgentEntity(self.agent_repository)
        self.store_agent_obj = StoreAgentObj(self.storage_agent_obj)

        self.store_agent_in_memory = StoreAgentInMemory(self.agent_manager)
        self.initial_simple_rag_agent = InitialSimpleRagAgent(
            self.store_agent_in_memory
        )
        self.create_simple_rag_handler = CreateSimpleRagAgent(
            self.uploaded_document_handler,
            self.add_document_to_agent,
            self.create_agent_entity,
            self.store_agent_obj,
            self.initial_simple_rag_agent,
        )

    async def create_simple_rag_agent(
        self, agent_data: CreateAgent, file: Optional[UploadFile] = None
    ):
        try:
            get_user_id = self.current_user_id()
            if not get_user_id:
                raise UserNotFoundException("none")

            agent_data_dict = agent_data.to_dict()
            print(f"Agent_data: {agent_data_dict}")

            # Create simple rag agent process
            agent = await self.create_simple_rag_handler.execute(
                CreateSimpleRagAgentInput(
                    get_user_id,
                    agent_data.llm_provider,
                    agent_data_dict,
                    self.chroma_db_path,
                    file,
                )
            )

            if not agent.is_success():
                get_exception = agent.get_exception()
                get_error_message = agent.get_error()
                self.logger.error(
                    f"Error while creating simple rag agent: {get_error_message}"
                )
                if get_exception:
                    raise get_exception

            get_agent_data = agent.get_data()

            await self.db.commit()
            return get_agent_data
        except Exception as e:
            self.logger.error(
                f"Unexpected error while create simple rag agent: {str(e)}"
            )
            raise e
