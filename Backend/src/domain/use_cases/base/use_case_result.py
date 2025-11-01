"""
Use Case Result pattern for handling success and error states.
"""

from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class UseCaseResult(Generic[T]):
    """
    Result wrapper for use case execution.
    Provides a consistent way to handle success and error states.
    """

    def __init__(
        self,
        success: bool,
        data: Optional[T] = None,
        error: Optional[str] = None,
        error_code: Optional[str] = None,
        exception_type: Optional[Exception] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.error_code = error_code
        self.exception_type: Optional[Exception] = exception_type

    @classmethod
    def success_result(cls, data: T) -> "UseCaseResult[T]":
        """Create a successful result with data."""
        return cls(success=True, data=data)

    @classmethod
    def error_result(
        cls,
        error: str,
        exception_type: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ) -> "UseCaseResult[T]":
        """Create an error result with error message and optional error code."""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            exception_type=exception_type,
        )

    @classmethod
    def validation_error(cls, field: str, message: str) -> "UseCaseResult[T]":
        """Create a validation error result."""
        return cls(
            success=False,
            error=f"Validation error in {field}: {message}",
            error_code="VALIDATION_ERROR",
        )

    @classmethod
    def not_found_error(cls, resource: str, identifier: Any) -> "UseCaseResult[T]":
        """Create a not found error result."""
        return cls(
            success=False,
            error=f"{resource} with identifier '{identifier}' not found",
            error_code="NOT_FOUND",
        )

    @classmethod
    def unauthorized_error(
        cls, message: str = "Unauthorized access"
    ) -> "UseCaseResult[T]":
        """Create an unauthorized error result."""
        return cls(success=False, error=message, error_code="UNAUTHORIZED")

    def is_success(self) -> bool:
        """Check if the result is successful."""
        return self.success

    def is_error(self) -> bool:
        """Check if the result is an error."""
        return not self.success

    def get_data(self) -> Optional[T]:
        """Get the data if successful, None otherwise."""
        return self.data if self.success else None

    def get_exception(self) -> Exception | None:
        return self.exception_type

    def get_error(self) -> Optional[str]:
        """Get the error message if failed, None otherwise."""
        return self.error

    def get_error_code(self) -> Optional[str]:
        """Get the error code if failed, None otherwise."""
        return self.error_code

    def __bool__(self) -> bool:
        """Allow direct truthiness checks (True when success)."""
        return self.success

    def map(self, fn: Callable[[T], Any]) -> "UseCaseResult[Any]":
        """If success, transform the data using fn; otherwise propagate the error."""
        if not self.success:
            return UseCaseResult[Any](
                success=False,
                error=self.error,
                error_code=self.error_code,
                exception_type=self.exception_type,
            )
        try:
            return UseCaseResult.success_result(fn(self.data))  # type: ignore[arg-type]
        except Exception as e:
            # In case mapping throws, surface as error result with original data untouched
            return UseCaseResult[Any](
                success=False,
                error=str(e),
                exception_type=e,
            )

    def __repr__(self) -> str:
        status = "success" if self.success else "error"
        return (
            f"UseCaseResult(status={status}, "
            f"data={self.data!r}, error={self.error!r}, "
            f"error_code={self.error_code!r}, exception={type(self.exception_type).__name__ if self.exception_type else None})"
        )
