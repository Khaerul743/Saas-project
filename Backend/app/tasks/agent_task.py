import json
import os
import shutil
from typing import Optional, Literal

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.tasks import celery_app
from celery import current_task
from app.events.redis_event import EventType, Event, event_bus
from app.AI import simple_RAG_agent as AI
from app.controllers.document_controller import agents
from app.models.agent.agent_entity import Agent
from app.models.agent.simple_rag_model import CreateSimpleRAGAgent, SimpleRAGAgentOut, UpdateSimpleRAGAgent
from app.models.document.document_entity import Document
from app.utils.document_utils import write_document
from app.utils.error_utils import handle_database_error, handle_user_not_found
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned
from app.configs.database import SessionLocal
logger = get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.agent_tasks.create_simple_rag_agent")
def create_simple_rag_agent(self,file: Optional[UploadFile], agent_data: CreateSimpleRAGAgent, user_id: int):
    db = SessionLocal()
    task_id = self.request.id
    try:
        logger.info(f"Creating Simple RAG Agent for user {user_id}")
        current_task.update_state(state="PROGRESS", meta={"current":20, "total":100, "status":"Creating Simple RAG Agent"})

        # Create new agent in database
        new_agent = Agent(
            user_id=user_id,
            name=agent_data.name,
            avatar=agent_data.avatar,
            model=agent_data.model,
            role="simple RAG agent",  # Fixed role for Simple RAG Agent
            description=agent_data.description,
            base_prompt=agent_data.base_prompt,
            tone=agent_data.tone,
            short_term_memory=agent_data.short_term_memory,
            long_term_memory=agent_data.long_term_memory,
            status=agent_data.status,
        )

        # Add to database
        db.add(new_agent)
        db.flush()

        current_task.update_state(state="PROGRESS", meta={"current":40, "total":100, "status":"Initializing Simple RAG Agent"})
        # Create directory for agent documents
        directory_path = f"documents/user_{user_id}/agent_{new_agent.id}"
    
        # Initialize Simple RAG Agent instance
        if not str(new_agent.id) in agents:
            def init_agent():
                agents[str(new_agent.id)] = AI.Agent(
                    base_prompt=new_agent.base_prompt,
                    tone=new_agent.tone,
                    directory_path=directory_path,
                    chromadb_path="chroma_db",
                    collection_name=f"agent_{new_agent.id}",
                    model_llm=new_agent.model,
                    short_memory=agent_data.short_term_memory,
                )

            init_agent()
        current_task.update_state(state="PROGRESS", meta={"current":60, "total":100, "status":"Adding Document to Simple RAG Agent"})
        # Handle file upload if provided
        if file:
            try:
                # Write file to disk first
                content_type: Literal['pdf'] | Literal['txt'] | Literal['csv'] | Literal['excel'] = write_document(file, directory_path)
                file_path = os.path.join(directory_path, file.filename)
                
                # Create document record in database
                post_document = Document(
                    agent_id=new_agent.id,
                    file_name=file.filename,
                    content_type=content_type,
                )

                db.add(post_document)
                db.flush()
                
                # Try to add document to RAG system
                agents[str(new_agent.id)].add_document(
                    file.filename,
                    content_type,
                    str(post_document.id),
                )

                # If everything succeeds, commit the transaction
                db.commit()
                db.refresh(post_document)
                current_task.update_state(state="PROGRESS", meta={"current":80, "total":100, "status":"Committing Transaction"})
            except Exception as e:
                # Rollback database transaction
                db.rollback()
                
                # Remove physical file if it exists
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Rollback: Removed file {file_path} due to error")
                except Exception as file_err:
                    logger.error(f"Failed to remove file {file_path} during rollback: {file_err}")
                
                # Re-raise the original exception
                raise e
        else:
            # No file upload, just commit the agent creation
            db.commit()

        # Refresh to get the created agent with all fields
        db.refresh(new_agent)
        current_task.update_state(state="SUCCESS", meta={"current":100, "total":100, "status":"Completed"})
        return {
            "status":"completed",
            "agent_id":new_agent.id, 
            "message":"Simple RAG Agent created successfully",
            "file_name":file.filename,
            "task_id":task_id,
            "document_id":post_document.id,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Simple RAG Agent: {str(e)}")
        current_task.update_state(state="FAILURE", meta={"current":100, "total":100, "status":"Failed to create Simple RAG Agent"})
        raise e
    finally:
        db.close()