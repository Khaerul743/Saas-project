from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.config.limiter import limiter
from app.controllers.company_information_controller import (
    get_all_company_information,
    get_company_information_by_agent_id,
    get_company_information_by_id,
    update_company_information,
    update_company_information_by_agent_id,
)
from app.middlewares.auth_dependencies import role_required
from app.models.company_information.company_model import UpdateCompanyInformation
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/agent/company-information", tags=["company-information"]
)


@router.get("", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def getAllCompanyInformation(
    request: Request,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Get all company information for the authenticated user's agents.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with list of company information
    """
    try:
        company_infos = get_all_company_information(db, current_user)
        return success_response(
            "Getting all company information is successfully", company_infos
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.get("/agent/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def getCompanyInformationByAgentId(
    request: Request,
    agent_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Get company information for a specific agent.

    Args:
        request: FastAPI request object
        agent_id: ID of the agent
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with company information data
    """
    try:
        company_info = get_company_information_by_agent_id(db, agent_id, current_user)
        return success_response(
            "Getting company information is successfully", company_info
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.get("/{company_info_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def getCompanyInformationById(
    request: Request,
    company_info_id: int,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Get company information by its ID.

    Args:
        request: FastAPI request object
        company_info_id: ID of the company information
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with company information data
    """
    try:
        company_info = get_company_information_by_id(db, company_info_id, current_user)
        return success_response(
            "Getting company information is successfully", company_info
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.put("/{company_info_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def updateCompanyInformation(
    request: Request,
    company_info_id: int,
    update_data: UpdateCompanyInformation,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Update company information by its ID.

    Args:
        request: FastAPI request object
        company_info_id: ID of the company information to update
        update_data: Update data for company information
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with updated company information data
    """
    try:
        updated_company_info = update_company_information(
            db, company_info_id, update_data, current_user
        )
        return success_response(
            "Company information updated successfully", updated_company_info
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise


@router.put("/agent/{agent_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def updateCompanyInformationByAgentId(
    request: Request,
    agent_id: int,
    update_data: UpdateCompanyInformation,
    current_user: dict = Depends(role_required(["admin", "user"])),
    db: Session = Depends(get_db),
):
    """
    Update company information for a specific agent.

    Args:
        request: FastAPI request object
        agent_id: ID of the agent
        update_data: Update data for company information
        current_user: Current authenticated user (from JWT token)
        db: Database session

    Returns:
        ResponseAPI: Success response with updated company information data
    """
    try:
        updated_company_info = update_company_information_by_agent_id(
            db, agent_id, update_data, current_user
        )
        return success_response(
            "Company information updated successfully", updated_company_info
        )
    except Exception as e:
        # This will be handled by the global error handler middleware
        raise
