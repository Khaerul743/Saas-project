from typing import Optional

from sqlalchemy.orm import Session

from app.configs.database import SessionLocal
from app.events.loop_manager import run_async
from app.events.redis_event import Event, EventType, event_bus
from app.tasks import celery_app
from app.utils.logger import get_logger
from app.utils.event_utils import publish_agent_event
from app.utils.agent_utils import (
    add_document_to_agent,
    build_task_result,
    create_agent_entity,
    initialize_simple_rag_agent,
)
from app.utils.file_utils import (
    cleanup_file_on_error,
    create_agent_directory,
    save_uploaded_file,
)
from app.utils.file_utils import create_agent_directory
from app.models.document.document_entity import Document
from app.models.agent.simple_rag_model import CreateSimpleRAGAgent
from app.models.agent.agent_entity import Agent
from app.models.company_information.company_entity import CompanyInformation  # noqa: F401
from app.models.document.document_entity import Document # noqa: F401
from app.models.history_message.history_entity import HistoryMessage  # noqa: F401
from app.models.history_message.metadata_entity import Metadata  # noqa: F401
from app.models.integration.integration_entity import Integration  # noqa: F401
from app.models.platform.platform_entity import Platform  # noqa: F401
from app.models.user.api_key_entity import ApiKey  # noqa: F401
from app.models.user.user_entity import User  # noqa: F401
from app.models.user_agent.user_agent_entity import UserAgent  # noqa: F401


logger = get_logger(__name__)

def _update_progress(task_instance, current: int, status: str, state: str = "PROGRESS"):
    """Update task progress"""
    task_instance.update_state(
        state=state, meta={"current": current, "total": 100, "status": status}
    )

    return {"current": current, "total": 100, "status": status}

def _handle_file_upload(
    task_instance, db: Session, agent: Agent, file_data: dict, directory_path: str
) -> int:
    """
    Handle file upload and document creation

    Args:
        task_instance: Celery task instance
        db: Database session
        agent: Agent entity
        file_data: File data dictionary
        directory_path: Directory path for files

    Returns:
        int: Document ID

    Raises:
        Exception: If file upload fails
    """
    file_path = None

    try:
        # Save file to disk
        file_path, content_type = save_uploaded_file(file_data, directory_path)

        # Create document record in database
        post_document = Document(
            agent_id=int(agent.id),  # type: ignore
            file_name=file_data["filename"],
            content_type=content_type,
        )

        db.add(post_document)
        db.flush()

        # Add document to AI agent
        add_document_to_agent(
            agent=agent,
            filename=file_data["filename"],
            content_type=content_type,
            document_id=int(post_document.id),  # type: ignore
        )

        # Update progress
        _update_progress(task_instance, 80, "Committing Transaction")

        return int(post_document.id)  # type: ignore

    except Exception as e:
        # Cleanup file on error
        if file_path:
            cleanup_file_on_error(file_path)
        raise e

@celery_app.task(bind=True, name="app.tasks.agent_task.create_simple_rag_agent")
def create_simple_rag_agent_task(self, file_data: Optional[dict], agent_data: dict, user_id: int):
    task_id = self.request.id
    db = SessionLocal()
    logger.info(f"Task Execution: user_id {user_id}")

    try:
        logger.info(f"Creating Simple RAG Agent for user {user_id}")
        # Step 1: Initialize task
        progress = _update_progress(self, 20, status="Initialize agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        # Step 2: Parse agent data
        agent_data_obj = CreateSimpleRAGAgent(**agent_data)
        logger.info(f"Agent data: {agent_data_obj}")
        # Step 3: Create agent entity
        new_agent = create_agent_entity(agent_data_obj, user_id, agent_role="simple RAG agent")
        logger.info(f"New agent: {new_agent}")
        db.add(new_agent)
        db.flush()
        db.refresh(new_agent)

        # Step 5: Initialize AI agent
        progress = _update_progress(self, 40, "Initializing Simple RAG Agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        directory_path = create_agent_directory(user_id, int(new_agent.id))  # type: ignore
        initialize_simple_rag_agent(new_agent, directory_path)

        # Step 6: Handle file upload if provided
        document_id = None
        if file_data:
            progress = _update_progress(self, 60, "Adding Document to Simple RAG Agent")
            publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
            document_id = _handle_file_upload(
                self, db, new_agent, file_data, directory_path
            )
        # Step 7: Commit transaction
        db.commit()
        db.refresh(new_agent)

        progress = _update_progress(self, 100, "Agent creation is completed", "SUCCESS")
        publish_agent_event(EventType.AGENT_CREATION_SUCCESS, user_id, 2, progress)
        return build_task_result(
            agent=new_agent,
            task_id=task_id,
            file_data=file_data,  # type: ignore
            document_id=document_id,  # type: ignore
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Simple RAG Agent: {str(e)}")
        progress = _update_progress(self, 100, "Agent creation is failed", "FAILURE")
        publish_agent_event(EventType.AGENT_CREATION_FAILURE, user_id, 2, progress)

        raise e
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.agent_task.create_customer_service_agent")
def create_customer_service_agent_task