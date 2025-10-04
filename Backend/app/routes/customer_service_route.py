import json
from typing import List

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.limiter import limiter
from app.controllers.customer_service_controller import (
    create_customer_service_agent,
    delete_customer_service_agent,
    get_customer_service_agent_by_id,
    update_customer_service_agent,
)
from app.middlewares.RBAC import role_required
from app.models.agent.customer_service_model import (
    CreateCustomerServiceAgent,
    CustomerServiceAgentResponse,
    CustomerServiceAgentAsyncResponse,
    DatasetDescription,
    UpdateCustomerServiceAgent,
)
from app.utils.response import success_response

router = APIRouter(prefix="/api/agents/customer-service", tags=["customer-service-agents"])


@router.post("", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def createCustomerServiceAgent(
    request: Request,
    files: List[UploadFile] = File(..., description="List of files (documents and datasets)"),
    agent_data: str = Form(..., description="Agent creation data as JSON string"),
    datasets: str = Form(..., description="Dataset descriptions as JSON string"),
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Create a new Customer Service Agent for the authenticated user.

    Args:
        request: FastAPI request object
        files: List of uploaded files (documents: PDF/TXT, datasets: CSV/Excel)
        agent_data: Customer Service Agent creation data from form
        datasets: Dataset descriptions as JSON string
        current_user: Current authenticated user (from JWT token)
        db: Database session
        background_tasks: Optional background tasks

    Returns:
        CustomerServiceAgentResponse: Success response with created Customer Service Agent data
        
    Example:
        agent_data: {
            "name": "Customer Support Bot",
            "model": "gpt-4o",
            "base_prompt": "You are a helpful customer service agent",
            "tone": "friendly",
            "short_term_memory": true,
            "long_term_memory": true,
            "status": "active"
        }
        
        datasets: [
            {
                "filename": "products",
                "description": "Database produk berisi informasi tentang produk perusahaan"
            },
            {
                "filename": "orders", 
                "description": "Database pesanan berisi informasi tentang pesanan pelanggan"
            }
        ]
    """
    try:
        # Parse agent data from form
        parsed_agent_data = json.loads(agent_data)
        
        # Parse datasets from form
        parsed_datasets = json.loads(datasets)
        
        # Validate required fields for Customer Service Agent
        if not parsed_agent_data.get("base_prompt"):
            raise ValueError("base_prompt is required for Customer Service Agent")
        if not parsed_agent_data.get("tone"):
            raise ValueError("tone is required for Customer Service Agent")
        
        # Validate files
        if not files:
            raise ValueError("At least one file is required (document or dataset)")
        
        # Validate datasets
        if not parsed_datasets:
            raise ValueError("Dataset descriptions are required for Customer Service Agent")
        
        # Validate that dataset descriptions match uploaded CSV/Excel files
        csv_excel_files = [f for f in files if f.filename.lower().endswith(('.csv', '.xlsx', '.xls'))]
        dataset_filenames = [d.get("filename") for d in parsed_datasets]
        
        for file in csv_excel_files:
            filename_without_ext = file.filename.rsplit('.', 1)[0]
            if filename_without_ext not in dataset_filenames:
                raise ValueError(f"Dataset description missing for file: {file.filename}")
        
        # Set default role
        parsed_agent_data["role"] = "customer service"
        
        # Convert datasets to DatasetDescription objects
        dataset_objects = [DatasetDescription(**d) for d in parsed_datasets]
        
        created_agent = await create_customer_service_agent(
            db,
            files,
            CreateCustomerServiceAgent(**parsed_agent_data),
            dataset_objects,
            current_user,
        )
        
        # Return success response
        return success_response(
            message="Customer Service Agent created successfully",
            data=created_agent
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.put("/{agent_id}", response_model=CustomerServiceAgentResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def updateCustomerServiceAgent(
    request: Request,
    agent_id: str,
    agent_data: UpdateCustomerServiceAgent,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Update an existing Customer Service Agent for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the Customer Service Agent to update
        agent_data: Customer Service Agent update data from request body
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        CustomerServiceAgentResponse: Success response with updated Customer Service Agent data
    """
    try:
        # Update Customer Service Agent using controller
        updated_agent = update_customer_service_agent(db, agent_id, agent_data, current_user)

        # Return success response
        return success_response(
            message="Customer Service Agent updated successfully", 
            data=updated_agent
        )

    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.get("/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def getCustomerServiceAgentById(
    request: Request,
    agent_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Get a Customer Service Agent by its ID for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the Customer Service Agent to retrieve
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        CustomerServiceAgentResponse: Success response with agent data
    """
    try:
        agent = get_customer_service_agent_by_id(db, agent_id, current_user)
        return success_response("Customer Service Agent retrieved successfully", agent)
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def deleteCustomerServiceAgent(
    request: Request,
    agent_id: str,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Delete a Customer Service Agent for the authenticated user.

    Args:
        request: FastAPI request object
        agent_id: ID of the Customer Service Agent to delete
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        Success response message
    """
    try:
        response = delete_customer_service_agent(agent_id, current_user, db)
        return success_response(response.get("message"))
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise
