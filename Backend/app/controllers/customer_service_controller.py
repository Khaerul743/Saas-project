import json
import os
import shutil
from typing import Dict, List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.AI import customer_service as AI
from app.AI.utils import dataset
from app.controllers.document_controller import agents
from app.dependencies.redis_storage import redis_storage
from app.models.agent.agent_entity import Agent
from app.models.agent.customer_service_model import (
    CreateCustomerServiceAgent,
    CustomerServiceAgentAsyncResponse,
    CustomerServiceAgentOut,
    DatasetDescription,
    UpdateCustomerServiceAgent,
)
from app.models.company_information.company_entity import CompanyInformation
from app.models.company_information.company_model import CreateCompanyInformation
from app.models.document.document_entity import Document
from app.utils.agent_utils import generate_agent_id
from app.utils.document_utils import write_document
from app.utils.error_utils import handle_database_error, handle_user_not_found
from app.utils.file_utils import create_agent_directory, get_content_type, process_file
from app.dependencies.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned

logger = get_logger(__name__)


async def create_customer_service_agent(
    db: Session,
    files: List[UploadFile],
    agent_data: CreateCustomerServiceAgent,
    datasets: List[DatasetDescription],
    current_user: dict,
):
    """
    Create a new Customer Service Agent for the authenticated user.

    Args:
        db: Database session
        files: List of uploaded files (documents and datasets)
        agent_data: Customer Service Agent creation data
        datasets: List of dataset descriptions
        current_user: Current authenticated user

    Returns:
        CustomerServiceAgentAsyncResponse: Async response with task ID

    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))
        generate_id = generate_agent_id(db)
        directory_path = create_agent_directory(user_id, generate_id)
        available_databases, dataset_descriptions, detail_data_parts = process_file(
            files, directory_path, datasets
        )

        company_information = CreateCompanyInformation(
            name=agent_data.company_name,
            industry=agent_data.industry,
            description=agent_data.company_description,
            address=agent_data.address,
            email=agent_data.email,
            website=agent_data.website,
            fallback_email=agent_data.fallback_email,
        )

        # Store data agent ke redis
        await redis_storage.store_agent(
            generate_id,
            {
                "base_prompt": str(agent_data.base_prompt),
                "tone": str(agent_data.tone),
                "directory_path": directory_path,
                "chromadb_path": "chroma_db",
                "collection_name": f"agent_{generate_id}",
                "llm_model": str(agent_data.model),
                "short_memory": bool(agent_data.short_term_memory),
                "long_memory": bool(agent_data.long_term_memory),
                "company_information": company_information.dict(),
                "status": "active",
                "role": "customer service agent",
                "available_databases": available_databases,
                "detail_data": detail_data_parts,
                "dataset_descriptions": dataset_descriptions,
            },
        )

        # Convert Pydantic model to dict untuk JSON serialization
        agent_data_dict = agent_data.dict()
        agent_data_dict["id"] = generate_id

        # # Handle files data untuk serialization

        files_data = []
        if files:
            for file in files:
                print(f"=== DEBUG FILE: {file.filename} ===")
                print(f"File size: {file.size}")
                print(f"Content type: {file.content_type}")

                # Read file content
                content_type = get_content_type(file)
                print(f"Detected content_type: {content_type}")

                if content_type in ["pdf", "txt"]:
                    print("=================================================W")
                    print(f"Processing file: {file.filename}")
                    print("=================================================")

                    # Check file position before reading
                    print(
                        f"File position before read: {file.file.tell() if hasattr(file.file, 'tell') else 'unknown'}"
                    )

                    # RESET FILE POINTER TO BEGINNING BEFORE READING
                    await file.seek(0)
                    print(
                        f"File position after seek(0): {file.file.tell() if hasattr(file.file, 'tell') else 'unknown'}"
                    )

                    file_content = await file.read()
                    print(f"File content length: {len(file_content)}")
                    print(f"File content (first 100 bytes): {file_content[:100]}")

                    if len(file_content) == 0:
                        print("ERROR: File content is empty!")
                        continue

                    file_data = {
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "content": file_content.hex(),  # Convert binary to hex string
                        "size": len(file_content),
                    }
                    files_data.append(file_data)

                    # Reset file pointer for potential future use
                    await file.seek(0)

        # print(f"agent_data: {agent_data_dict}")
        # print(f"dataset dict: {datasets_dict}")
        # # Import task function
        from app.tasks.test_task import create_customer_service_agent_task

        # # # # Start Celery task dengan data yang sudah di-serialize
        task = create_customer_service_agent_task.delay(
            files_data=files_data,  # List of file data dicts
            agent_data=agent_data_dict,  # Dict instead of Pydantic model
            # datasets=datasets_dict,  # List of dataset dicts
            user_id=user_id,
        )

        # Return response dengan format yang sesuai untuk async task
        return {
            "id": generate_id,  # Will be set when task completes
            "name": agent_data.name,
            "avatar": agent_data.avatar,
            "model": agent_data.model,
            "description": agent_data.description,
            "base_prompt": agent_data.base_prompt,
            "tone": agent_data.tone,
            "short_term_memory": agent_data.short_term_memory,
            "long_term_memory": agent_data.long_term_memory,
            "status": "pending",  # Override status untuk async task
            "created_at": None,  # Will be set when task completes
            "task_id": task.id,
            "message": "Customer Service Agent creation is pending",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while starting Customer Service Agent creation: {str(e)}",
            exc_info=True,
        )
        raise handle_database_error(
            e, "starting Customer Service Agent creation", current_user.get("email")
        )


async def update_customer_service_agent(
    db: Session,
    agent_id: str,
    agent_data: UpdateCustomerServiceAgent,
    current_user: dict,
) -> CustomerServiceAgentOut:
    """
    Update an existing Customer Service Agent and its company information.

    Args:
        db: Database session
        agent_id: ID of the agent to update
        agent_data: Update data including agent and company information
        current_user: Current authenticated user

    Returns:
        CustomerServiceAgentOut: Updated agent data

    Raises:
        HTTPException: If update fails
    """
    try:
        # Validate agent exists and is owned by user
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        # Check if agent is Customer Service Agent
        if agent.role != "customer service":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for Customer Service Agents.",
            )

        # Separate agent fields from company information fields
        update_data = agent_data.dict(exclude_unset=True)
        agent_fields = {}
        company_fields = {}

        # Define company information field names
        company_field_names = {
            "company_name",
            "industry",
            "company_description",
            "address",
            "email",
            "website",
            "fallback_email",
        }

        # Separate fields
        for field, value in update_data.items():
            if field in company_field_names:
                company_fields[field] = value
            else:
                agent_fields[field] = value

        # Update agent fields
        for field, value in agent_fields.items():
            if hasattr(agent, field):
                setattr(agent, field, value)

        # Update company information if provided
        if company_fields:
            # Get or create company information
            company_info = (
                db.query(CompanyInformation)
                .filter(CompanyInformation.agent_id == agent_id)
                .first()
            )

            if not company_info:
                # Create new company information if it doesn't exist
                company_info = CompanyInformation(
                    agent_id=agent_id,
                    name=company_fields.get("company_name", ""),
                    industry=company_fields.get("industry", ""),
                    description=company_fields.get("company_description", ""),
                    address=company_fields.get("address", ""),
                    email=company_fields.get("email", ""),
                    website=company_fields.get("website"),
                    fallback_email=company_fields.get("fallback_email", ""),
                )
                db.add(company_info)
            else:
                # Update existing company information
                for field, value in company_fields.items():
                    # Map company field names to database field names
                    db_field_mapping = {
                        "company_name": "name",
                        "company_description": "description",
                    }
                    db_field = db_field_mapping.get(field, field)
                    if hasattr(company_info, db_field):
                        setattr(company_info, db_field, value)

        # Commit changes to database
        db.commit()
        db.refresh(agent)
        if company_fields:
            db.refresh(company_info)

        # Update agent object in memory if it exists
        try:
            from app.controllers.document_controller import agents

            agent_id_str = str(agent_id)

            if agent_id_str in agents:
                # Update agent object properties
                if agent_fields:
                    for field, value in agent_fields.items():
                        if hasattr(agents[agent_id_str], field):
                            setattr(agents[agent_id_str], field, value)

                # Update company information in agent object
                if company_fields:
                    # Get updated company information
                    updated_company_info = {
                        "name": company_info.name,
                        "industry": company_info.industry,
                        "description": company_info.description,
                        "address": company_info.address,
                        "email": company_info.email,
                        "website": company_info.website,
                        "fallback_email": company_info.fallback_email,
                    }

                    # Update agent's company_information
                    if hasattr(agents[agent_id_str], "company_information"):
                        setattr(
                            agents[agent_id_str],
                            "company_information",
                            updated_company_info,
                        )
                        logger.info(
                            f"Updated company_information in agent {agent_id_str} object"
                        )
                    else:
                        # Try to set the attribute even if it doesn't exist
                        setattr(
                            agents[agent_id_str],
                            "company_information",
                            updated_company_info,
                        )
                        logger.info(
                            f"Set company_information attribute in agent {agent_id_str} object"
                        )

                logger.info(f"Updated agent {agent_id_str} object in memory")
            else:
                logger.info(
                    f"Agent {agent_id_str} not found in memory, skipping agent object update"
                )

        except Exception as agent_update_error:
            # Log error but don't fail the update
            logger.warning(f"Failed to update agent object: {str(agent_update_error)}")

        # Update agent data in Redis storage if exists
        try:
            update_redis = await redis_storage.update_customer_service_agent(
                agent_id, update_data
            )
            if update_redis:
                logger.info(f"Updated agent {agent_id} in Redis storage")
            else:
                logger.info(
                    f"Agent {agent_id} not found in Redis storage, skipping Redis update"
                )
        except Exception as redis_error:
            # Log error but don't fail the update
            logger.warning(f"Failed to update agent in Redis: {str(redis_error)}")

        logger.info(
            f"Customer Service Agent '{agent.name}' (ID: {agent.id}) updated successfully by user "
            f"{current_user.get('email')}"
        )

        return CustomerServiceAgentOut(
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
            f"Unexpected error while updating Customer Service Agent: {str(e)}",
            exc_info=True,
        )
        raise handle_database_error(
            e, "updating Customer Service Agent", current_user.get("email")
        )


def get_customer_service_agent_by_id(
    db: Session,
    agent_id: str,
    current_user: dict,
) -> dict:
    """
    Get a Customer Service Agent by its ID including company information.

    Args:
        db: Database session
        agent_id: ID of the agent to retrieve
        current_user: Current authenticated user

    Returns:
        dict: Agent data with company information

    Raises:
        HTTPException: If agent not found or unauthorized
    """
    try:
        # Validate agent exists and is owned by user
        agent = validate_agent_exists_and_owned(
            db, agent_id, current_user.get("id"), current_user.get("email")
        )

        # Check if agent is Customer Service Agent
        if agent.role != "customer service":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for Customer Service Agents.",
            )

        # Get company information for the agent
        company_info = (
            db.query(CompanyInformation)
            .filter(CompanyInformation.agent_id == agent_id)
            .first()
        )

        # Prepare response data
        response_data = {
            "id": agent.id,
            "name": agent.name,
            "avatar": agent.avatar,
            "model": agent.model,
            "description": agent.description,
            "base_prompt": agent.base_prompt,
            "tone": agent.tone,
            "short_term_memory": agent.short_term_memory,
            "long_term_memory": agent.long_term_memory,
            "status": agent.status,
            "created_at": agent.created_at,
            "company_information": None,
        }

        # Add company information if exists
        if company_info:
            response_data["company_information"] = {
                "id": company_info.id,
                "agent_id": company_info.agent_id,
                "name": company_info.name,
                "industry": company_info.industry,
                "description": company_info.description,
                "address": company_info.address,
                "email": company_info.email,
                "website": company_info.website,
                "fallback_email": company_info.fallback_email,
                "created_at": company_info.created_at,
            }

        logger.info(
            f"Customer Service Agent '{agent.name}' (ID: {agent.id}) with company information retrieved successfully by user "
            f"{current_user.get('email')}"
        )

        return response_data

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving Customer Service Agent: {str(e)}",
            exc_info=True,
        )
        raise handle_database_error(
            e, "retrieving Customer Service Agent", current_user.get("email")
        )


def delete_customer_service_agent(
    agent_id: str,
    current_user: dict,
    db: Session,
) -> dict:
    """
    Delete a Customer Service Agent.

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

        # Check if agent is Customer Service Agent
        if agent.role != "customer service":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is only for Customer Service Agents.",
            )

        # Remove agent from memory if exists
        if str(agent_id) in agents:
            del agents[str(agent_id)]

        # Delete agent from database (cascade will handle related records)
        db.delete(agent)
        db.commit()

        logger.info(
            f"Customer Service Agent '{agent.name}' (ID: {agent_id}) deleted successfully by user "
            f"{current_user.get('email')}"
        )

        return {
            "message": f"Customer Service Agent deleted successfully: agent ID is {agent_id}"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while deleting Customer Service Agent: {str(e)}",
            exc_info=True,
        )
        raise handle_database_error(
            e, "deleting Customer Service Agent", current_user.get("email")
        )
