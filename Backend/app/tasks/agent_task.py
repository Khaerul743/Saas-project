import json
import os
import shutil
from typing import Literal, Optional

# from celery import current_task  # Not needed since we use bind=True
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.AI import simple_RAG_agent as AI
from app.configs.database import SessionLocal
from app.controllers.document_controller import agents
from app.events.redis_event import Event, EventType, event_bus
from app.models.agent.agent_entity import Agent
from app.models.agent.simple_rag_model import (
    CreateSimpleRAGAgent,
    SimpleRAGAgentOut,
    UpdateSimpleRAGAgent,
)
from app.models.document.document_entity import Document
# Import related models to ensure they are registered
from app.models.company_information.company_entity import CompanyInformation  # noqa: F401
from app.models.platform.platform_entity import Platform  # noqa: F401
from app.models.integration.integration_entity import Integration  # noqa: F401
from app.models.history_message.history_entity import HistoryMessage  # noqa: F401
from app.models.history_message.metadata_entity import Metadata  # noqa: F401
from app.models.user_agent.user_agent_entity import UserAgent  # noqa: F401
from app.models.user.api_key_entity import ApiKey  # noqa: F401
from app.tasks import celery_app
from app.utils.document_utils import write_document
from app.utils.error_utils import handle_database_error, handle_user_not_found
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned

logger = get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.agent_task.create_simple_rag_agent")
def create_simple_rag_agent(
    self, file_data: Optional[dict], agent_data: dict, user_id: int
):
    db = SessionLocal()
    task_id = self.request.id
    try:
        logger.info(f"Creating Simple RAG Agent for user {user_id}")
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Creating Simple RAG Agent"},
        )

        # Convert dict back to Pydantic model
        agent_data_obj = CreateSimpleRAGAgent(**agent_data)

        # Create new agent in database
        new_agent = Agent(
            user_id=user_id,
            name=agent_data_obj.name,
            avatar=agent_data_obj.avatar,
            model=agent_data_obj.model,
            role="simple RAG agent",  # Fixed role for Simple RAG Agent
            description=agent_data_obj.description,
            base_prompt=agent_data_obj.base_prompt,
            tone=agent_data_obj.tone,
            short_term_memory=agent_data_obj.short_term_memory,
            long_term_memory=agent_data_obj.long_term_memory,
            status=agent_data_obj.status,
        )

        # Add to database
        db.add(new_agent) 
        db.flush()
        db.refresh(new_agent)  # Refresh to get the actual values

        self.update_state(
            state="PROGRESS",
            meta={
                "current": 40,
                "total": 100,
                "status": "Initializing Simple RAG Agent",
            },
        )
        # Create directory for agent documents
        directory_path = f"documents/user_{user_id}/agent_{new_agent.id}"
        
        # Ensure directory exists
        os.makedirs(directory_path, exist_ok=True)

        # Initialize Simple RAG Agent instance
        if not str(new_agent.id) in agents:

            def init_agent():
                agents[str(new_agent.id)] = AI.Agent(
                    base_prompt=str(new_agent.base_prompt),  # type: ignore
                    tone=str(new_agent.tone),  # type: ignore
                    directory_path=directory_path,
                    chromadb_path="chroma_db",
                    collection_name=f"agent_{new_agent.id}",
                    model_llm=str(new_agent.model),  # type: ignore
                    short_memory=agent_data_obj.short_term_memory,
                )

            init_agent()
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 60,
                "total": 100,
                "status": "Adding Document to Simple RAG Agent",
            },
        )
        # Handle file upload if provided
        if file_data:
            try:
                # Recreate file from serialized data
                file_path = os.path.join(directory_path, file_data["filename"])

                # Write file content from hex string
                file_content = bytes.fromhex(file_data["content"])
                with open(file_path, "wb") as f:
                    f.write(file_content)

                # Determine content type
                content_type = (
                    "pdf" if file_data["content_type"] == "application/pdf" else "txt"
                )

                # Create document record in database
                post_document = Document(
                    agent_id=new_agent.id,
                    file_name=file_data["filename"],
                    content_type=content_type,
                )

                db.add(post_document)
                db.flush()

                # Try to add document to RAG system
                agents[str(new_agent.id)].add_document(
                    file_data["filename"],
                    content_type,
                    str(post_document.id),
                )

                # If everything succeeds, commit the transaction
                db.commit()
                db.refresh(post_document)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": 80,
                        "total": 100,
                        "status": "Committing Transaction",
                    },
                )
            except Exception as e:
                # Rollback database transaction
                db.rollback()

                # Remove physical file if it exists
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Rollback: Removed file {file_path} due to error")
                except Exception as file_err:
                    logger.error(
                        f"Failed to remove file {file_path} during rollback: {file_err}"
                    )

                # Re-raise the original exception
                raise e
        else:
            # No file upload, just commit the agent creation
            db.commit()

        # Refresh to get the created agent with all fields
        db.refresh(new_agent)
        self.update_state(
            state="SUCCESS", meta={"current": 100, "total": 100, "status": "Completed"}
        )
        result = {
            "status": "completed",
            "agent_id": new_agent.id,
            "message": "Simple RAG Agent created successfully",
            "task_id": task_id,
        }
        # Add file info if file was uploaded
        if file_data:
            result["file_name"] = file_data["filename"]
            # Check if post_document exists in local scope
            if "post_document" in locals():
                result["document_id"] = post_document.id

        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Simple RAG Agent: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "current": 100,
                "total": 100,
                "status": "Failed to create Simple RAG Agent",
            },
        )
        raise e
    finally:
        db.close()
