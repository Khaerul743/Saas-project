# """
# Celery task for creating Simple RAG Agent
# """

# import asyncio
# from typing import Optional

# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy.orm import Session

# from app.configs.database import SessionLocal
# from app.events.redis_event import Event, EventType, event_bus
# from app.models.agent.agent_entity import Agent
# from app.models.agent.simple_rag_model import CreateSimpleRAGAgent

# # Import related models to ensure they are registered
# from app.models.company_information.company_entity import (
#     CompanyInformation,  # noqa: F401
# )
# from app.models.document.document_entity import Document
# from app.models.history_message.history_entity import HistoryMessage  # noqa: F401
# from app.models.history_message.metadata_entity import Metadata  # noqa: F401
# from app.models.integration.integration_entity import Integration  # noqa: F401
# from app.models.platform.platform_entity import Platform  # noqa: F401
# from app.models.user.api_key_entity import ApiKey  # noqa: F401
# from app.models.user_agent.user_agent_entity import UserAgent  # noqa: F401
# from app.tasks import celery_app
# from app.utils.agent_utils import (
#     add_document_to_agent,
#     build_task_result,
#     create_agent_entity,
#     initialize_ai_agent,
# )
# from app.utils.event_utils import (
#     publish_agent_failure_event,
#     publish_agent_progress_event,
#     publish_agent_success_event,
# )
# from app.utils.file_utils import (
#     cleanup_file_on_error,
#     create_agent_directory,
#     save_uploaded_file,
# )
# from app.utils.logger import get_logger

# # Import handlers to ensure they are registered in Celery worker
# # from app.events import handlers  # noqa: F401

# logger = get_logger(__name__)


# @celery_app.task(bind=True, name="app.tasks.agent_task.create_simple_rag_agent")
# def create_simple_rag_agent(
#     self, file_data: Optional[dict], agent_data: dict, user_id: int
# ):
#     """
#     Create a Simple RAG Agent with optional document upload

#     Args:
#         self: Celery task instance
#         file_data: Optional file data dictionary
#         agent_data: Agent creation data dictionary
#         user_id: ID of the user creating the agent

#     Returns:
#         dict: Task result with agent information
#     """
#     db = SessionLocal()
#     task_id = self.request.id
#     new_agent = None

#     try:
#         logger.info(f"Creating Simple RAG Agent for user {user_id}")

#         # Step 1: Initialize task
#         _update_progress(self, 20, "Creating Simple RAG Agent")

#         # Step 2: Parse agent data
#         agent_data_obj = CreateSimpleRAGAgent(**agent_data)

#         # Step 3: Create agent entity
#         new_agent = create_agent_entity(agent_data_obj, user_id)
#         db.add(new_agent)
#         db.flush()
#         db.refresh(new_agent)

#         # Step 4: Publish progress event
#         publish_agent_progress_event(
#             user_id=user_id,
#             agent_id=int(new_agent.id),  # type: ignore
#             current=40,
#             total=100,
#             status="Initializing Simple RAG Agent",
#             task_id=task_id,
#         )

#         # Step 5: Initialize AI agent
#         _update_progress(self, 40, "Initializing Simple RAG Agent")
#         directory_path = create_agent_directory(user_id, int(new_agent.id))  # type: ignore
#         initialize_ai_agent(new_agent, directory_path)

#         # Step 6: Handle file upload if provided
#         document_id = None
#         if file_data:
#             _update_progress(self, 60, "Adding Document to Simple RAG Agent")
#             document_id = _handle_file_upload(
#                 self, db, new_agent, file_data, directory_path
#             )

#         # Step 7: Commit transaction
#         db.commit()
#         db.refresh(new_agent)

#         # Step 8: Publish success event
#         publish_agent_success_event(
#             user_id=user_id,
#             agent_id=int(new_agent.id),  # type: ignore
#             additional_data={"document_id": document_id} if document_id else None,
#             task_id=task_id,
#         )

#         # Step 9: Complete task
#         _update_progress(self, 100, "Completed")

#         return build_task_result(
#             agent=new_agent,
#             task_id=task_id,
#             file_data=file_data,  # type: ignore
#             document_id=document_id,  # type: ignore
#         )

#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error creating Simple RAG Agent: {str(e)}")

#         # Publish failure event
#         publish_agent_failure_event(
#             user_id=user_id,
#             agent_id=int(new_agent.id) if new_agent else 0,  # type: ignore
#             error_message=str(e),
#             task_id=task_id,
#         )

#         _update_progress(self, 100, "Failed to create Simple RAG Agent", "FAILURE")
#         raise e

#     finally:
#         db.close()


# def _update_progress(task_instance, current: int, status: str, state: str = "PROGRESS"):
#     """Update task progress"""
#     task_instance.update_state(
#         state=state, meta={"current": current, "total": 100, "status": status}
#     )
#     return


# def _handle_file_upload(
#     task_instance, db: Session, agent: Agent, file_data: dict, directory_path: str
# ) -> int:
#     """
#     Handle file upload and document creation

#     Args:
#         task_instance: Celery task instance
#         db: Database session
#         agent: Agent entity
#         file_data: File data dictionary
#         directory_path: Directory path for files

#     Returns:
#         int: Document ID

#     Raises:
#         Exception: If file upload fails
#     """
#     file_path = None

#     try:
#         # Save file to disk
#         file_path, content_type = save_uploaded_file(file_data, directory_path)

#         # Create document record in database
#         post_document = Document(
#             agent_id=int(agent.id),  # type: ignore
#             file_name=file_data["filename"],
#             content_type=content_type,
#         )

#         db.add(post_document)
#         db.flush()

#         # Add document to AI agent
#         add_document_to_agent(
#             agent=agent,
#             filename=file_data["filename"],
#             content_type=content_type,
#             document_id=int(post_document.id),  # type: ignore
#         )

#         # Update progress
#         _update_progress(task_instance, 80, "Committing Transaction")

#         return int(post_document.id)  # type: ignore

#     except Exception as e:
#         # Cleanup file on error
#         if file_path:
#             cleanup_file_on_error(file_path)
#         raise e
