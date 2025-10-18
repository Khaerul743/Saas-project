"""
Error response formatting utilities.
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status


def format_error_response(
    error_code: str,
    message: str,
    field: Optional[str] = None,
    value: Optional[Any] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Dict[str, Any]:
    """
    Format error response in a consistent structure.
    
    Args:
        error_code: Error code identifier
        message: Human-readable error message
        field: Field that caused the error (optional)
        value: Value that caused the error (optional)
        status_code: HTTP status code
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "status": "error",
        "error": error_code,
        "message": message
    }
    
    if field:
        response["field"] = field
    
    if value is not None:
        response["value"] = value
    
    return response


def create_validation_error_response(
    field: str,
    message: str,
    value: Optional[Any] = None
) -> HTTPException:
    """
    Create a validation error response.
    
    Args:
        field: Field that failed validation
        message: Validation error message
        value: Value that failed validation
        
    Returns:
        HTTPException with formatted error response
    """
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=format_error_response(
            error_code="VALIDATION_ERROR",
            message=message,
            field=field,
            value=value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    )


def create_bad_request_error_response(
    error_code: str,
    message: str,
    field: Optional[str] = None,
    value: Optional[Any] = None
) -> HTTPException:
    """
    Create a bad request error response.
    
    Args:
        error_code: Error code identifier
        message: Error message
        field: Field that caused the error
        value: Value that caused the error
        
    Returns:
        HTTPException with formatted error response
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=format_error_response(
            error_code=error_code,
            message=message,
            field=field,
            value=value,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    )


def create_internal_server_error_response(
    message: str = "An unexpected error occurred. Please try again later."
) -> HTTPException:
    """
    Create an internal server error response.
    
    Args:
        message: Error message
        
    Returns:
        HTTPException with formatted error response
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=format_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )


def create_not_found_error_response(
    resource: str,
    identifier: Optional[str] = None
) -> HTTPException:
    """
    Create a not found error response.
    
    Args:
        resource: Type of resource not found
        identifier: Identifier of the resource
        
    Returns:
        HTTPException with formatted error response
    """
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"
    
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=format_error_response(
            error_code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    )


def create_unauthorized_error_response(
    message: str = "Authentication required"
) -> HTTPException:
    """
    Create an unauthorized error response.
    
    Args:
        message: Error message
        
    Returns:
        HTTPException with formatted error response
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=format_error_response(
            error_code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    )
