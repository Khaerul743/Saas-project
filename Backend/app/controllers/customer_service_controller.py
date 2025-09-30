import json
import os
import shutil
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.AI import customer_service as AI
from app.AI.utils import dataset
from app.controllers.document_controller import agents
from app.models.agent.agent_entity import Agent
from app.models.agent.customer_service_model import (
    CreateCustomerServiceAgent,
    CustomerServiceAgentOut,
    DatasetDescription,
    UpdateCustomerServiceAgent,
)
from app.models.company_information.company_entity import CompanyInformation
from app.models.company_information.company_model import CreateCompanyInformation
from app.models.document.document_entity import Document
from app.utils.document_utils import write_document
from app.utils.error_utils import handle_database_error, handle_user_not_found
from app.utils.logger import get_logger
from app.utils.validation_utils import validate_agent_exists_and_owned

logger = get_logger(__name__)


def get_filename_without_extension(filename: str) -> str:
    """Extract filename without extension"""
    return os.path.splitext(filename)[0]


def process_dataset_info(file_path: str, filename: str) -> str:
    """Process dataset and get info using get_dataset_info"""
    try:
        filename_without_ext = get_filename_without_extension(filename)
        return dataset.get_dataset_info(file_path, filename_without_ext)
    except Exception as e:
        logger.error(f"Error processing dataset info for {filename}: {str(e)}")
        return f"Error processing dataset {filename}: {str(e)}"


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
        background_tasks: Optional background tasks

    Returns:
        CustomerServiceAgentOut: Created agent data

    Raises:
        HTTPException: If creation fails
    """
    try:
        # ✅ Removed debug print statement
        # Validate user exists
        user_id = current_user.get("id")
        if not user_id:
            raise handle_user_not_found(current_user.get("email", "unknown"))

        agent_data_dict = agent_data.dict()

        # Create new agent in database
        new_agent = Agent(
            user_id=user_id,
            name=agent_data.name,
            avatar=agent_data.avatar,
            model=agent_data.model,
            role="customer service",  # Fixed role for Customer Service Agent
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

        # Add company information to database
        new_company_information = CompanyInformation(
            agent_id=new_agent.id,
            name=agent_data.company_name,
            industry=agent_data.industry,
            description=agent_data.company_description,
            address=agent_data.address,
            email=agent_data.email,
            website=agent_data.website,
            fallback_email=agent_data.fallback_email,
        )
        db.add(new_company_information)

        # Create directory for agent documents
        directory_path = f"documents/user_{user_id}/agent_{new_agent.id}"

        # Process files and create document records
        document_records = []
        available_databases = []
        dataset_descriptions = {}
        detail_data_parts = []

        for file in files:
            try:
                # Write file to disk
                content_type = write_document(file, directory_path)
                file_path = os.path.join(directory_path, file.filename)

                # Create document record
                post_document = Document(
                    agent_id=new_agent.id,
                    file_name=file.filename,
                    content_type=content_type,  # ✅ Fixed: Use dynamic content_type
                )

                db.add(post_document)
                db.flush()
                document_records.append(post_document)

                # Process CSV/Excel files for dataset info
                if content_type in ["csv", "excel"]:
                    filename_without_ext = get_filename_without_extension(file.filename)
                    available_databases.append(filename_without_ext)

                    # Get dataset description from user input
                    dataset_desc = next(
                        (d for d in datasets if d.filename == filename_without_ext),
                        None,
                    )

                    if dataset_desc:
                        dataset_descriptions[
                            f"db_{filename_without_ext}_description"
                        ] = dataset_desc.description

                    # Create database file in the same directory as documents
                    db_path = os.path.join(directory_path, f"{filename_without_ext}.db")
                    try:
                        # Create database from CSV/Excel file
                        dataset.get_dataset(
                            file_path,
                            db_path,
                            f"SELECT * FROM {filename_without_ext}",
                            filename_without_ext,
                        )
                        logger.info(f"Created database {db_path} from {file.filename}")
                    except Exception as e:
                        logger.error(
                            f"Failed to create database for {file.filename}: {str(e)}"
                        )

                    # Get dataset info for detail_data
                    try:
                        dataset_info = process_dataset_info(file_path, file.filename)
                        detail_data_parts.append(dataset_info)
                    except Exception as e:
                        logger.warning(
                            f"Could not process dataset info for {file.filename}: {str(e)}"
                        )
                        detail_data_parts.append(
                            f"Dataset {file.filename}: Unable to process dataset information"
                        )

                # For PDF/TXT files, add to RAG system
                elif content_type in ["pdf", "txt"]:
                    pass

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

                raise e
        print(f"document records: {document_records}")
        # Initialize Customer Service Agent instance
        if not str(new_agent.id) in agents:

            def init_agent():
                # Prepare kwargs with dataset descriptions
                agent_kwargs = {**dataset_descriptions}

                company_information = CreateCompanyInformation(
                    name=agent_data.company_name,
                    industry=agent_data.industry,
                    description=agent_data.company_description,
                    address=agent_data.address,
                    email=agent_data.email,
                    website=agent_data.website,
                    fallback_email=agent_data.fallback_email,
                )
                # ✅ Removed debug print statements
                agents[str(new_agent.id)] = AI.Agent(
                    base_prompt=agent_data.base_prompt,
                    tone=agent_data.tone,
                    llm_model=agent_data.model,
                    directory_path=directory_path,
                    chromadb_path="chroma_db",
                    collection_name=f"agent_{new_agent.id}",
                    available_databases=available_databases,
                    detail_data="\n".join(detail_data_parts)
                    if detail_data_parts
                    else "",
                    company_information=company_information,
                    long_memory=agent_data.long_term_memory,
                    short_memory=agent_data.short_term_memory,
                    **agent_kwargs,
                )

            init_agent()

        print(f"agents: {agents[str(new_agent.id)].company_information}")

        # Add PDF/TXT documents to RAG system
        for doc_record in document_records:
            if doc_record.content_type in ["pdf", "txt"]:
                logger.info(
                    f"Adding {doc_record.content_type} file {doc_record.file_name} to RAG system"
                )
                try:
                    agents[str(new_agent.id)].add_document(
                        doc_record.file_name,
                        doc_record.content_type,
                        str(doc_record.id),
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to add document {doc_record.file_name} to RAG system: {str(e)}"
                    )
                    # Continue with other documents even if one fails

        # Commit all changes
        db.commit()
        db.refresh(new_agent)

        logger.info(
            f"Customer Service Agent '{new_agent.name}' (ID: {new_agent.id}) created successfully by user "
            f"{current_user.get('email')} with {len(available_databases)} datasets and {len(document_records)} documents"
        )

        return CustomerServiceAgentOut(
            id=new_agent.id,
            name=new_agent.name,
            avatar=new_agent.avatar,
            model=new_agent.model,
            description=new_agent.description,
            base_prompt=new_agent.base_prompt,
            tone=new_agent.tone,
            short_term_memory=new_agent.short_term_memory,
            long_term_memory=new_agent.long_term_memory,
            status=new_agent.status,
            created_at=new_agent.created_at,
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError while creating Customer Service Agent: {str(e)}")
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
            f"Unexpected error while creating Customer Service Agent: {str(e)}",
            exc_info=True,
        )
        raise handle_database_error(
            e, "creating Customer Service Agent", current_user.get("email")
        )


def update_customer_service_agent(
    db: Session,
    agent_id: int,
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

        logger.info(
            f"Customer Service Agent '{agent.name}' (ID: {agent.id}) updated successfully by user "
            f"{current_user.get('email')}"
        )

        print(f"agents: {agents[agent_id_str].company_information}")

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
    agent_id: int,
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
    agent_id: int,
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
