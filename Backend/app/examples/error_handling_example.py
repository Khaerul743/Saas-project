"""
Contoh penggunaan error handling pattern untuk register endpoint.
File ini menunjukkan bagaimana error handling bekerja dalam berbagai skenario.
"""

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    EmailAlreadyExistsException,
    InvalidEmailFormatException,
    PasswordTooWeakException,
    ValidationException,
    DatabaseException,
)
from app.models.auth.auth_model import RegisterModel
from app.services.auth_service import AuthService


async def example_register_handler(db: AsyncSession, payload: RegisterModel):
    """
    Contoh register handler dengan error handling yang baik.
    """
    try:
        auth = AuthService(db)
        new_user = await auth.register_user(payload)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": new_user
        }
        
    except EmailAlreadyExistsException as e:
        # Error 400: Email sudah ada
        # Response: {"status": "error", "error": "EMAIL_ALREADY_EXISTS", "message": "Email is already registered", "field": "email", "value": "user@example.com"}
        raise e
        
    except (InvalidEmailFormatException, PasswordTooWeakException, ValidationException) as e:
        # Error 400/422: Validasi gagal
        # Response: {"status": "error", "error": "INVALID_EMAIL_FORMAT", "message": "Invalid email format", "field": "email", "value": "invalid-email"}
        raise e
        
    except DatabaseException as e:
        # Error 500: Database error
        # Response: {"status": "error", "error": "DATABASE_ERROR", "message": "Database user creation failed: Connection timeout", "field": "database"}
        raise e
        
    except Exception as e:
        # Error 500: Unexpected error
        # Response: {"status": "error", "error": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred. Please try again later.", "field": "server"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "field": "server"
            }
        )


# Contoh skenario error yang akan terjadi:

"""
1. EMAIL ALREADY EXISTS
Request: POST /api/register
{
    "email": "existing@example.com",
    "password": "ValidPass123!",
    "username": "testuser"
}

Response: 400 Bad Request
{
    "status": "error",
    "error": "EMAIL_ALREADY_EXISTS",
    "message": "Email is already registered",
    "field": "email",
    "value": "existing@example.com"
}

2. INVALID EMAIL FORMAT
Request: POST /api/register
{
    "email": "invalid-email",
    "password": "ValidPass123!",
    "username": "testuser"
}

Response: 400 Bad Request
{
    "status": "error",
    "error": "INVALID_EMAIL_FORMAT",
    "message": "Invalid email format",
    "field": "email",
    "value": "invalid-email"
}

3. PASSWORD TOO WEAK
Request: POST /api/register
{
    "email": "user@example.com",
    "password": "weak",
    "username": "testuser"
}

Response: 400 Bad Request
{
    "status": "error",
    "error": "PASSWORD_TOO_WEAK",
    "message": "Password must be at least 6 characters long",
    "field": "password"
}

4. USERNAME VALIDATION ERROR
Request: POST /api/register
{
    "email": "user@example.com",
    "password": "ValidPass123!",
    "username": "a"
}

Response: 422 Unprocessable Entity
{
    "status": "error",
    "error": "VALIDATION_ERROR",
    "message": "Username must be at least 2 characters long",
    "field": "username",
    "value": "a"
}

5. DATABASE ERROR
Request: POST /api/register
{
    "email": "user@example.com",
    "password": "ValidPass123!",
    "username": "testuser"
}

Response: 500 Internal Server Error
{
    "status": "error",
    "error": "DATABASE_ERROR",
    "message": "Database user creation failed: Connection timeout",
    "field": "database"
}

6. SUCCESS
Request: POST /api/register
{
    "email": "newuser@example.com",
    "password": "mypassword123",
    "username": "testuser"
}

Response: 200 OK
{
    "status": "success",
    "message": "User registered successfully",
    "data": {
        "id": 1,
        "name": "testuser",
        "email": "newuser@example.com",
        "plan": "free"
    }
}
"""
