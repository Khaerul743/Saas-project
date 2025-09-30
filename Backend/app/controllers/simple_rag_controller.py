import json
import os
import shutil
from typing import Optional

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.AI import simple_RAG_agent as AI
from app.controllers.document_controller import agents

# from app.events.redis_event import event_bus
# from app.models.agent.agent_entity import Agent
from app.models.agent.simple_rag_model import (
    CreateSimpleRAGAgent,
    SimpleRAGAgentAsyncResponse,
    SimpleRAGAgentOut,
    UpdateSimpleRAGAgent,
)
from app.models.document.document_entity import Document
from app.tasks import celery_app
from app.tasks.test_task import create_simple_rag_agent_task
from app.utils.document_utils import write_document
from app.utils.error_utils import handle_database_error, handle_user_not_found
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned

logger = get_logger(__name__)


async def create_simple_rag_agent(
    db: Session,
    file: Optional[UploadFile],
    agent_data: CreateSimpleRAGAgent,
    current_user: dict,
) -> SimpleRAGAgentAsyncResponse:
    """
    Create a new Simple RAG Agent for the authenticated user.

    Args:
        db: Database session
        file: Optional uploaded file for document
        agent_data: Simple RAG Agent creation data
        current_user: Current authenticated user
        background_tasks: Optional background tasks

    Returns:
        SimpleRAGAgentOut: Created agent data

    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))

        # if file:
        #     if file.content_type not in ["pdf", "txt"]:
        #         raise HTTPException(
        #             status_code=status.HTTP_400_BAD_REQUEST,
        #             detail="File type must be pdf or txt.",
        #         )

        # Convert Pydantic model to dict untuk JSON serialization
        agent_data_dict = agent_data.dict()

        # Handle file data untuk serialization
        file_data = None
        if file:
            # Read file content
            file_content = await file.read()
            file_data = {
                "filename": file.filename,
                "content_type": file.content_type,
                "content": file_content.hex(),  # Convert binary to hex string
                "size": len(file_content),
            }
            # Reset file pointer
            await file.seek(0)

        # Start Celery task dengan data yang sudah di-serialize
        # task = create_simple_rag_agent_task.delay(
        #     file_data=file_data,  # Dict instead of UploadFile
        #     agent_data=agent_data_dict,  # Dict instead of Pydantic model
        #     user_id=user_id
        # )
        task = create_simple_rag_agent_task.delay(
            file_data=file_data, agent_data=agent_data_dict, user_id=user_id
        )
        # Return response dengan format yang sesuai untuk async task
        return SimpleRAGAgentAsyncResponse(
            id=None,  # Will be set when task completes
            name=agent_data.name,
            avatar=agent_data.avatar,
            model=agent_data.model,
            description=agent_data.description,
            base_prompt=agent_data.base_prompt,
            tone=agent_data.tone,
            short_term_memory=agent_data.short_term_memory,
            long_term_memory=agent_data.long_term_memory,
            status="pending",  # Override status untuk async task
            created_at=None,  # Will be set when task completes
            task_id=task.id,
            message="Simple RAG Agent creation is pending",
        )
        # Create new agent in database
        # new_agent = Agent(
        #     user_id=user_id,
        #     name=agent_data.name,
        #     avatar=agent_data.avatar,
        #     model=agent_data.model,
        #     role="simple RAG agent",  # Fixed role for Simple RAG Agent
        #     description=agent_data.description,
        #     base_prompt=agent_data.base_prompt,
        #     tone=agent_data.tone,
        #     short_term_memory=agent_data.short_term_memory,
        #     long_term_memory=agent_data.long_term_memory,
        #     status=agent_data.status,
        # )

        # # Add to database
        # db.add(new_agent)
        # db.flush()

        # # Create directory for agent documents
        # directory_path = f"documents/user_{user_id}/agent_{new_agent.id}"

        # # Initialize Simple RAG Agent instance
        # if not str(new_agent.id) in agents:
        #     def init_agent():
        #         agents[str(new_agent.id)] = AI.Agent(
        #             base_prompt=new_agent.base_prompt,
        #             tone=new_agent.tone,
        #             directory_path=directory_path,
        #             chromadb_path="chroma_db",
        #             collection_name=f"agent_{new_agent.id}",
        #             model_llm=new_agent.model,
        #             short_memory=agent_data.short_term_memory,
        #         )

        #     init_agent()

        # # Handle file upload if provided
        # if file:
        #     try:
        #         # Write file to disk first
        #         content_type: Literal['pdf'] | Literal['txt'] | Literal['csv'] | Literal['excel'] = write_document(file, directory_path)
        #         file_path = os.path.join(directory_path, file.filename)

        #         # Create document record in database
        #         post_document = Document(
        #             agent_id=new_agent.id,
        #             file_name=file.filename,
        #             content_type=content_type,
        #         )

        #         db.add(post_document)
        #         db.flush()

        #         # Try to add document to RAG system
        #         agents[str(new_agent.id)].add_document(
        #             file.filename,
        #             content_type,
        #             str(post_document.id),
        #         )

        #         # If everything succeeds, commit the transaction
        #         db.commit()
        #         db.refresh(post_document)

        #     except Exception as e:
        #         # Rollback database transaction
        #         db.rollback()

        #         # Remove physical file if it exists
        #         try:
        #             if os.path.exists(file_path):
        #                 os.remove(file_path)
        #                 logger.info(f"Rollback: Removed file {file_path} due to error")
        #         except Exception as file_err:
        #             logger.error(f"Failed to remove file {file_path} during rollback: {file_err}")

        #         # Re-raise the original exception
        #         raise e
        # else:
        #     # No file upload, just commit the agent creation
        #     db.commit()

        # # Refresh to get the created agent with all fields
        # db.refresh(new_agent)

        # logger.info(
        #     f"Simple RAG Agent '{new_agent.name}' (ID: {new_agent.id}) created successfully by user "
        #     f"{current_user.get('email')}"
        # )

        # return SimpleRAGAgentOut(
        #     id=new_agent.id,
        #     name=new_agent.name,
        #     avatar=new_agent.avatar,
        #     model=new_agent.model,
        #     description=new_agent.description,
        #     base_prompt=new_agent.base_prompt,
        #     tone=new_agent.tone,
        #     short_term_memory=new_agent.short_term_memory,
        #     long_term_memory=new_agent.long_term_memory,
        #     status=new_agent.status,
        #     created_at=new_agent.created_at,
        # )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError while creating Simple RAG Agent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists or invalid data provided.",
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while creating Simple RAG Agent: {str(e)}", exc_info=True
        )
        raise handle_database_error(
            e, "creating Simple RAG Agent", current_user.get("email")
        )


def update_simple_rag_agent(
    db: Session,
    agent_id: int,
    agent_data: UpdateSimpleRAGAgent,
    current_user: dict,
) -> SimpleRAGAgentOut:
    """
    Update an existing Simple RAG Agent.

    Args:
        db: Database session
        agent_id: ID of the agent to update
        agent_data: Update data
        current_user: Current authenticated user

    Returns:
        SimpleRAGAgentOut: Updated agent data

    Raises:
        HTTPException: If update fails
    """
    try:
        # Validate agent exists and is owned by user
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        # Check if agent is Simple RAG Agent
        if agent.role != "simple RAG agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for Simple RAG Agents.",
            )

        # Update agent fields
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)

        db.commit()
        db.refresh(agent)

        logger.info(
            f"Simple RAG Agent '{agent.name}' (ID: {agent.id}) updated successfully by user "
            f"{current_user.get('email')}"
        )

        return SimpleRAGAgentOut(
            id=agent.id,
            name=agent.name,
            avatar=agent.avatar,
            model=agent.model,
            description=agent.description,
            base_prompt=agent.base_prompt,
            tone=agent.tone,
            short_term_memory=agent.short_term_memory,
            long_term_memory=agent.long_term_memory,
            status=agent.status,
            created_at=agent.created_at,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while updating Simple RAG Agent: {str(e)}", exc_info=True
        )
        raise handle_database_error(
            e, "updating Simple RAG Agent", current_user.get("email")
        )


def delete_simple_rag_agent(
    agent_id: int,
    current_user: dict,
    db: Session,
) -> dict:
    """
    Delete a Simple RAG Agent.

    Args:
        agent_id: ID of the agent to delete
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Validate agent exists and is owned by user
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        # Check if agent is Simple RAG Agent
        if agent.role != "simple RAG agent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for Simple RAG Agents.",
            )

        # Remove agent from memory if exists
        if str(agent_id) in agents:
            del agents[str(agent_id)]

        # Delete agent from database (cascade will handle related records)
        db.delete(agent)
        db.commit()

        logger.info(
            f"Simple RAG Agent '{agent.name}' (ID: {agent_id}) deleted successfully by user "
            f"{current_user.get('email')}"
        )

        return {
            "message": f"Simple RAG Agent deleted successfully: agent ID is {agent_id}"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while deleting Simple RAG Agent: {str(e)}", exc_info=True
        )
        raise handle_database_error(
            e, "deleting Simple RAG Agent", current_user.get("email")
        )
