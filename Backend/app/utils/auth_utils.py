from fastapi import HTTPException, status


def email_exists_handler(logger, email: str):
    """
    Handle error when email is already registered.
    
    Args:
        logger: Logger instance
        email: Email that already exists
    """
    logger.warning(f"Email is already in use: {email}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Email is already in use."
    )


def email_not_found_handler(logger, email: str):
    """
    Handle error when email is not registered.
    
    Args:
        logger: Logger instance
        email: Email that was not found
    """
    logger.warning(f"Email not found: {email}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Email is not registered. Please check your email or register first."
    )


def invalid_credentials_handler(logger, email: str):
    """
    Handle error when login credentials are invalid (email exists but password is wrong).
    
    Args:
        logger: Logger instance
        email: Email that had invalid credentials
    """
    logger.warning(f"Invalid login attempt for email: {email}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. Please check your email and password."
    )


def authentication_failed_handler(logger, email: str, reason: str = "Invalid credentials"):
    """
    Generic handler for authentication failures.
    
    Args:
        logger: Logger instance
        email: Email that failed authentication
        reason: Reason for authentication failure
    """
    logger.warning(f"Authentication failed for email: {email} - Reason: {reason}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication failed. Please check your credentials."
    )