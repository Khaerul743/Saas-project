# Error Handling Pattern

Dokumen ini menjelaskan pola error handling yang digunakan dalam aplikasi untuk memberikan response error yang konsisten dan informatif kepada client.

## Struktur Error Response

Semua error response mengikuti struktur yang konsisten:

```json
{
  "status": "error",
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "field": "field_name", // optional
  "value": "problematic_value" // optional
}
```

## Custom Exception Classes

### 1. AuthException (Base)
Base class untuk semua authentication-related exceptions.

### 2. EmailAlreadyExistsException
- **Status Code**: 400 Bad Request
- **Error Code**: EMAIL_ALREADY_EXISTS
- **Use Case**: Ketika user mencoba register dengan email yang sudah ada

### 3. EmailNotFoundException
- **Status Code**: 404 Not Found
- **Error Code**: EMAIL_NOT_FOUND
- **Use Case**: Ketika user mencoba login dengan email yang tidak ada

### 4. InvalidCredentialsException
- **Status Code**: 401 Unauthorized
- **Error Code**: INVALID_CREDENTIALS
- **Use Case**: Ketika password salah saat login

### 5. PasswordTooWeakException
- **Status Code**: 400 Bad Request
- **Error Code**: PASSWORD_TOO_WEAK
- **Use Case**: Ketika password tidak memenuhi kriteria dasar (minimal 6 karakter, tidak terlalu umum)

### 6. InvalidEmailFormatException
- **Status Code**: 400 Bad Request
- **Error Code**: INVALID_EMAIL_FORMAT
- **Use Case**: Ketika format email tidak valid

### 7. ValidationException
- **Status Code**: 422 Unprocessable Entity
- **Error Code**: VALIDATION_ERROR
- **Use Case**: Ketika input data tidak valid

### 8. DatabaseException
- **Status Code**: 500 Internal Server Error
- **Error Code**: DATABASE_ERROR
- **Use Case**: Ketika terjadi error pada operasi database

## Error Handling Pattern di Controller

```python
async def endpoint_handler(db: AsyncSession, payload: Model):
    try:
        service = ServiceClass(db)
        result = await service.method(payload)
        return result
        
    except SpecificException as e:
        # Log warning untuk expected errors
        logger.warning(f"Expected error: {str(e.detail)}")
        raise e  # Re-raise untuk FastAPI handling
        
    except DatabaseException as e:
        # Log error untuk database issues
        logger.error(f"Database error: {str(e.detail)}")
        raise e
        
    except Exception as e:
        # Log error untuk unexpected issues
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "field": "server"
            }
        )
```

## Error Handling Pattern di Service

```python
async def service_method(self, payload: Model):
    try:
        # Validate input
        validated_data = validate_data(payload)
        
        # Business logic
        result = await self.repository.method(validated_data)
        
        return result
        
    except (SpecificException, ValidationException):
        # Re-raise custom exceptions
        raise
    except SQLAlchemyError as e:
        # Convert database errors to custom exceptions
        logger.error(f"Database error: {str(e)}")
        raise DatabaseException("operation", str(e))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise DatabaseException("operation", "An unexpected error occurred")
```

## Validation Pattern

```python
def validate_input(data: str) -> str:
    if not data or not isinstance(data, str):
        raise ValidationException("field", "Field is required")
    
    if len(data) < 2:
        raise ValidationException("field", "Field must be at least 2 characters")
    
    return data.strip()
```

## Logging Pattern

- **INFO**: Successful operations
- **WARNING**: Expected errors (validation, business logic)
- **ERROR**: Unexpected errors, database issues
- **DEBUG**: Detailed debugging information

## Contoh Response Error

### 1. Email Already Exists
```json
{
  "status": "error",
  "error": "EMAIL_ALREADY_EXISTS",
  "message": "Email is already registered",
  "field": "email",
  "value": "user@example.com"
}
```

### 2. Password Too Weak
```json
{
  "status": "error",
  "error": "PASSWORD_TOO_WEAK",
  "message": "Password must be at least 6 characters long",
  "field": "password"
}
```

### 3. Database Error
```json
{
  "status": "error",
  "error": "DATABASE_ERROR",
  "message": "Database user creation failed: Connection timeout",
  "field": "database"
}
```

### 4. Internal Server Error
```json
{
  "status": "error",
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred. Please try again later.",
  "field": "server"
}
```

## Best Practices

1. **Specific Exceptions**: Gunakan exception yang spesifik untuk setiap jenis error
2. **Consistent Structure**: Semua error response harus mengikuti struktur yang sama
3. **Proper Logging**: Log dengan level yang sesuai untuk setiap jenis error
4. **User-Friendly Messages**: Berikan pesan error yang mudah dipahami user
5. **Field Information**: Sertakan informasi field yang menyebabkan error
6. **Security**: Jangan expose informasi sensitif dalam error message
7. **Error Codes**: Gunakan error code yang konsisten untuk client handling
