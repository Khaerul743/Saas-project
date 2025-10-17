from typing import Optional, List

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
from app.dependencies.redis_storage import redis_storage
from app.events.loop_manager import run_async


logger = get_logger(__name__)

def _update_progress(task_instance, current: int, status: str, state: str = "PROGRESS"):
    """Update task progress"""
    task_instance.update_state(
        state=state, meta={"current": current, "total": 100, "status": status}
    )

    return {"current": current, "total": 100, "status": status}

def _handle_file_upload(
    task_instance, db: Session, agent_id: str, file_data: dict, directory_path: str
) -> int:
    """
    Handle file upload and document creation

    Args:
        task_instance: Celery task instance
        db: Database session
        agent_id: Agent ID
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
            agent_id=agent_id,  # type: ignore
            file_name=file_data["filename"],
            content_type=content_type,
        )

        db.add(post_document)
        db.flush()

        # Add document to AI agent
        add_document_to_agent(
            directory_path=directory_path,
            agent_id=agent_id,
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
        logger.info(f"Creating Simple RAG Agent for user {user_id}: {agent_data['id']}")
        # Step 1: Initialize task
        progress = _update_progress(self, 20, status="Initialize agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data['id'], progress)
        # Step 2: Parse agent data
        agent_data_obj = CreateSimpleRAGAgent(**agent_data)
        logger.info(f"Agent data: {agent_data_obj}")
        # Step 3: Create agent entity
        new_agent = create_agent_entity(agent_data_obj, user_id, agent_role="simple RAG agent")
        logger.info(f"New agent: {new_agent}")
        db.add(new_agent)

        # Step 5: Initialize AI agent
        progress = _update_progress(self, 40, "Initializing Simple RAG Agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data['id'], progress)
        directory_path = create_agent_directory(user_id, agent_data['id'])  # type: ignore
        
        # initialize_simple_rag_agent(new_agent, directory_path)

        # Step 6: Handle file upload if provided
        document_id = None
        if file_data:
            progress = _update_progress(self, 60, "Adding Document to Simple RAG Agent")
            publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data['id'], progress)
            document_id = _handle_file_upload(
                self, db, agent_data['id'], file_data, directory_path
            )
        # Step 7: Commit transaction
        db.commit()

        progress = _update_progress(self, 80, "Agent creation is completed", "SUCCESS")
        publish_agent_event(EventType.AGENT_CREATION_SUCCESS, user_id, agent_data['id'], progress)

        return build_task_result(
            agent=new_agent,
            task_id=task_id,
            file_data=file_data,  # type: ignore
            document_id=document_id,  # type: ignore
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Simple RAG Agent: {str(e)}")
        
        # Handle specific error types
        error_message = "Agent creation failed"
        if "Duplicate entry" in str(e) and "PRIMARY" in str(e):
            error_message = "Agent with this ID already exists. Please try again."
            logger.warning(f"Duplicate agent ID detected: {agent_data.get('id', 'unknown')}")
        elif "IntegrityError" in str(e):
            error_message = "Database constraint violation. Please check your data."
        
        progress = _update_progress(self, 100, error_message, "FAILURE")
        publish_agent_event(EventType.AGENT_CREATION_FAILURE, user_id, agent_data.get('id', 'unknown'), progress)

        raise e
    finally:
        db.close()


# @celery_app.task(bind=True, name="app.tasks.agent_task.create_customer_service_agent")
# def create_customer_service_agent_task(self, files_data: Optional[List[dict]], agent_data: dict, datasets: List[dict], user_id: int):
#     task_id = self.request.id
#     db = SessionLocal()
#     logger.info(f"Task Execution: user_id {user_id}")

#     try:
#         logger.info(f"Creating Customer Service Agent for user {user_id}")
        
#         # Step 1: Initialize task
#         progress = _update_progress(self, 10, status="Initialize Customer Service Agent")
#         publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        
#         # Step 2: Parse agent data
#         from app.models.agent.customer_service_model import CreateCustomerServiceAgent
#         agent_data_obj = CreateCustomerServiceAgent(**agent_data)
#         logger.info(f"Agent data: {agent_data_obj}")
        
#         # Step 3: Create agent entity
#         new_agent = create_agent_entity(agent_data_obj, user_id, agent_role="customer service")
#         logger.info(f"New agent: {new_agent}")
#         db.add(new_agent)
#         db.flush()
#         db.refresh(new_agent)

#         # Step 4: Create company information
#         progress = _update_progress(self, 20, "Creating company information")
#         publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        
#         from app.models.company_information.company_entity import CompanyInformation
#         new_company_information = CompanyInformation(
#             agent_id=new_agent.id,
#             name=agent_data_obj.company_name,
#             industry=agent_data_obj.industry,
#             description=agent_data_obj.company_description,
#             address=agent_data_obj.address,
#             email=agent_data_obj.email,
#             website=agent_data_obj.website,
#             fallback_email=agent_data_obj.fallback_email,
#         )
#         db.add(new_company_information)
#         db.flush()

#         # Step 5: Create agent directory
#         progress = _update_progress(self, 30, "Creating agent directory")
#         publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        
#         directory_path = create_agent_directory(user_id, int(new_agent.id))  # type: ignore

#         # Step 6: Initialize Customer Service Agent
#         progress = _update_progress(self, 40, "Initializing Customer Service Agent")
#         publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        
#         from app.utils.agent_utils import initialize_customer_service_agent
#         initialize_customer_service_agent(new_agent, directory_path, agent_data_obj, datasets)

#         # Step 7: Handle file uploads if provided
#         document_ids = []
#         if files_data:
#             progress = _update_progress(self, 60, "Processing uploaded files")
#             publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
            
#             document_ids = _handle_customer_service_files(
#                 self, db, new_agent, files_data, directory_path, datasets
#             )

#         # Step 8: Commit transaction
#         progress = _update_progress(self, 90, "Committing transaction")
#         publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, 2, progress)
        
#         db.commit()
#         db.refresh(new_agent)

#         # Step 9: Success
#         progress = _update_progress(self, 100, "Customer Service Agent creation completed", "SUCCESS")
#         publish_agent_event(EventType.AGENT_CREATION_SUCCESS, user_id, 2, progress)
        
#         return build_task_result(
#             agent=new_agent,
#             task_id=task_id,
#             file_data=files_data[0] if files_data else None,
#             document_ids=document_ids,
#         )
        
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error creating Customer Service Agent: {str(e)}")
#         progress = _update_progress(self, 100, "Customer Service Agent creation failed", "FAILURE")
#         publish_agent_event(EventType.AGENT_CREATION_FAILURE, user_id, 2, progress)
#         raise e
#     finally:
#         db.close()

@celery_app.task(bind=True, name="app.tasks.agent_task.create_customer_service_agent")
def create_customer_service_agent_task(self, files_data: Optional[List[dict]], agent_data: dict, user_id: int):
    task_id = self.request.id
    db = SessionLocal()
    logger.info(f"Task Execution: user_id {user_id}")
    
    try:
        from app.models.agent.customer_service_model import CreateCustomerServiceAgent
        # Step 2: Parse agent data
        agent_data_obj = CreateCustomerServiceAgent(**agent_data)
        logger.info(f"Creating Customer Service Agent for user {user_id}")
        progress = _update_progress(self, 10, status="Initialize Customer Service Agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)

        logger.info(f"Agent data: {agent_data_obj}")

#         # Step 3: Create agent entity
        new_agent = create_agent_entity(agent_data_obj, user_id, agent_role="customer service")
        logger.info(f"New agent: {new_agent}")
        db.add(new_agent)

#         # Step 4: Create company information
        progress = _update_progress(self, 20, "Creating company information")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)
        
        from app.models.company_information.company_entity import CompanyInformation
        new_company_information = CompanyInformation(
            agent_id=agent_data_obj.id,
            name=agent_data_obj.company_name,
            industry=agent_data_obj.industry,
            description=agent_data_obj.company_description,
            address=agent_data_obj.address,
            email=agent_data_obj.email,
            website=agent_data_obj.website,
            fallback_email=agent_data_obj.fallback_email,
        )
        db.add(new_company_information)
        db.flush()

#         # Step 5: Create agent directory
        progress = _update_progress(self, 30, "Creating agent directory")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)
        
        directory_path = create_agent_directory(user_id, agent_data_obj.id)  # type: ignore
    
#         # Step 6: Initialize Customer Service Agent
        progress = _update_progress(self, 40, "Initializing Customer Service Agent")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)
        
        from app.utils.agent_utils import initialize_customer_service_agent
        # initialized_agent = initialize_customer_service_agent(new_agent, directory_path, agent_data_obj, datasets)
        # run_async(redis_storage.store_agent(str(new_agent.id), initialized_agent))
#         # Step 7: Handle file uploads if provided
        document_ids = []
        if files_data:
            print("=============================================================================================================================\n")
            progress = _update_progress(self, 60, "Processing uploaded files")
            publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)
            
            document_ids = _handle_customer_service_files(
                self, db, agent_data_obj.id, files_data, directory_path
            )
    
#         # Step 8: Commit transaction
        progress = _update_progress(self, 70, "Committing transaction")
        publish_agent_event(EventType.AGENT_CREATION_PROGRESS, user_id, agent_data_obj.id, progress)
        
        db.commit()
        db.refresh(new_agent)

#         # Step 9: Success
        progress = _update_progress(self, 80, "Customer Service Agent creation completed", "SUCCESS")
        publish_agent_event(EventType.AGENT_CREATION_SUCCESS, user_id, agent_data_obj.id, progress)
        
        return build_task_result(
            agent=new_agent,
            task_id=task_id,
            file_data=files_data[0] if files_data else None,
            document_ids=document_ids,
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Customer Service Agent: {str(e)}")
        progress = _update_progress(self, 100, "Customer Service Agent creation failed", "FAILURE")
        publish_agent_event(EventType.AGENT_CREATION_FAILURE, user_id, agent_data_obj.id, progress)
        raise e
    finally:
        db.close()

    
def _handle_customer_service_files(
    task_instance, 
    db: Session, 
    agent_id: str, 
    files_data: List[dict], 
    directory_path: str,
    # datasets: List[dict]
) -> List[int]:
    """
    Handle file uploads for Customer Service Agent
    
    Args:
        task_instance: Celery task instance
        db: Database session
        agent: Agent entity
        files_data: List of file data dictionaries
        directory_path: Directory path for files
        datasets: List of dataset descriptions
        
    Returns:
        List[int]: List of document IDs
        
    Raises:
        Exception: If file processing fails
    """
    document_ids = []
    available_databases = []
    dataset_descriptions = {}
    detail_data_parts = []
    
    try:
        from app.utils.file_utils import save_uploaded_file
        import os
        
        for file_data in files_data:
            try:
                # Write file to disk
                file_path, content_type = save_uploaded_file(file_data, directory_path)
                
                # Create document record
                post_document = Document(
                    agent_id=agent_id,  # type: ignore
                    file_name=file_data["filename"],
                    content_type=content_type,
                )
                
                db.add(post_document)
                db.flush()
                document_ids.append(int(post_document.id))  # type: ignore
                
                # Process CSV/Excel files for dataset info
                # if content_type in ["csv", "excel"]:
                #     logger.info(f"Processing {content_type} file: {file_data['filename']}")
                #     filename_without_ext = file_data["filename"].split('.')[0]
                #     available_databases.append(filename_without_ext)
                    
                #     # Get dataset description from user input
                #     dataset_desc = next(
                #         (d for d in datasets if d.get("filename") == filename_without_ext),
                #         None,
                #     )
                    
                #     if dataset_desc:
                #         dataset_descriptions[
                #             f"db_{filename_without_ext}_description"
                #         ] = dataset_desc.get("description", "")
                    
                #     # Create database file
                #     db_path = os.path.join(directory_path, f"{filename_without_ext}.db")
                #     try:
                #         get_dataset(
                #             file_path,
                #             db_path,
                #             f"SELECT * FROM {filename_without_ext}",
                #             filename_without_ext,
                #         )
                #         logger.info(f"Created database {db_path} from {file_data['filename']}")
                #     except Exception as e:
                #         logger.error(f"Failed to create database for {file_data['filename']}: {str(e)}")
                    
                #     # Get dataset info for detail_data
                #     detail_data_parts.append(f"Dataset {file_data['filename']}: Processed successfully")
                
                # For PDF/TXT files, add to RAG system
                if content_type in ["pdf", "txt"]:
                    logger.info(f"Processing {content_type} file for RAG: {file_data['filename']}")
                    from app.utils.agent_utils import add_document_to_agent
                    add_document_to_agent(
                        agent_id=agent_id,
                        filename=file_data["filename"],
                        content_type=content_type,
                        document_id=int(post_document.id),  # type: ignore
                        directory_path=directory_path,
                    )
                
                # Update progress
                current_progress = 60 + (len(document_ids) * 20 // len(files_data))
                _update_progress(task_instance, current_progress, f"Processing file {len(document_ids)}/{len(files_data)}")
                print("\n=============================================================================================================================")
            except Exception as e:
                # Cleanup file on error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        return document_ids
        
    except Exception as e:
        # Cleanup all files on error
        for file_data in files_data:
            file_path = os.path.join(directory_path, file_data["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
        raise e