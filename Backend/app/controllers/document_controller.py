import os
import shutil
from typing import Dict, List, Any

from fastapi import BackgroundTasks, Form, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.AI import simple_RAG_agent as AI
from app.models.agent.agent_entity import Agent
from app.models.document.document_entity import Document
from app.core.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned

logger = get_logger(__name__)

agents: Dict[str, Any] = {}


def get_documents_by_agent(
    agent_id: str, current_user: dict, db: Session
) -> List[Document]:
    try:
        # agent = (
        #     db.query(Agent)
        #     .filter(Agent.id == agent_id, Agent.user_id == current_user.get("id"))
        #     .first()
        # )
        # if not agent:
        #     logger.warning(
        #         f"Agent not found: user {current_user.get('email')}, agent ID {agent_id}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Agent not found",
        #     )
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        documents = db.query(Document).filter(Document.agent_id == agent_id).all()
        if not documents:
            logger.info(
                f"No documents found for agent ID {agent_id} by user {current_user.get('email')}"
            )
            return []

        logger.info(
            f"Retrieved {len(documents)} documents for agent '{agent.name}' (ID: {agent.id}) by user {current_user.get('email')}"
        )
        return documents

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving documents: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


async def document_store(
    file: UploadFile,
    agent_id: str,
    current_user: dict,
    db: Session,
    background_tasks: BackgroundTasks = None,
):
    try:
        if file.content_type == "application/pdf":
            content_type = "pdf"
        elif file.content_type == "application/txt":
            content_type = "txt"
        else:
            content_type = "docs"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be pdf or txt.",
            )
        # agent = (
        #     db.query(Agent)
        #     .filter(Agent.id == agent_id, Agent.user_id == current_user.get("id"))
        #     .first()
        # )
        # if not agent:
        #     logger.warning(
        #         f"Agent not found: user {current_user.get('email')}, agent ID {agent_id}"
        #     )
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        #     )
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        document = (
            db.query(Document)
            .filter(Document.file_name == file.filename, Document.agent_id == agent_id)
            .first()
        )
        if document:
            logger.warning(f"Document is exist: file name {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Document is exist"
            )
        directory_path = f"documents/user_{current_user.get('id')}/agent_{agent_id}"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

        file_path = os.path.join(directory_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        post_document = Document(
            agent_id=agent_id, file_name=file.filename, content_type=content_type
        )
        db.add(post_document)
        db.commit()
        db.refresh(post_document)
        if not str(agent.id) in agents:
            agents[str(agent.id)] = AI.Agent(
                directory_path,
                "chroma_db",
                f"agent_{agent_id}",
                model_llm=agent.model,
            )

        def init_agent():
            agents[str(agent.id)].add_document(
                file.filename,
                content_type,
                str(post_document.id),
                db,
                post_document,
                f"{directory_path}/{file.filename}",
            )
            agents[str(agent.id)].execute(
                {
                    "user_message": "Tolong jelaskan secara singkat isi dari document tersebut"
                },
                "thread_123",
            )

        init_agent()
        # background_tasks.add_task(init_agent)
        logger.info(
            f"Agent '{agent.name}' (ID: {agent.id}) document store successfully by user "
            f"{current_user.get('email')}"
        )
        return post_document
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError while add document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later.",
        )
    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while store the document: {str(e)}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )


def document_delete(document_id: int, agent_id: str, current_user: dict, db: Session):
    try:
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.agent_id == agent_id)
            .join(Agent, Document.agent_id == Agent.id)
            .filter(Agent.user_id == current_user.get("id"))
            .first()
        )
        if not document:
            logger.warning(
                f"Document not found: user {current_user.get('email')}, document ID {document_id}, agent ID {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        directory_path = f"documents/user_{current_user.get('id')}/agent_{agent_id}"
        file_path = os.path.join(directory_path, document.file_name)

        try:
            # Try to delete from RAG system first
            agents[str(current_user.get("id"))].delete_document(str(document.id))

            # If RAG deletion succeeds, delete from database
            db.delete(document)
            db.commit()

            # Finally, remove physical file
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed physical file: {file_path}")

        except Exception as e:
            # If RAG deletion fails, rollback database transaction
            db.rollback()
            logger.error(f"Failed to delete document from RAG system: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document from RAG system: {str(e)}",
            )
        logger.info(
            f"Document '{document.file_name}' (ID: {document.id}) deleted successfully by user {current_user.get('email')}"
        )
        return {"detail": "Document deleted successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while deleting the document: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error, please try again later",
        )
