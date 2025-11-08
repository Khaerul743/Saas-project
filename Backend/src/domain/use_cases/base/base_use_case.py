"""
Base use case class that all use cases should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .use_case_result import UseCaseResult

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class BaseUseCase(ABC, Generic[InputType, OutputType]):
    """
    Base class for all use cases.

    A use case represents a single business operation and encapsulates
    the business logic required to perform that operation.
    """

    @abstractmethod
    async def execute(self, input_data: InputType) -> UseCaseResult[OutputType]:
        """
        Execute the use case with the given input data.

        Args:
            input_data: The input data required for the use case

        Returns:
            UseCaseResult containing either the successful output or error information
        """
        pass

    def validate_input(self, input_data: InputType) -> UseCaseResult[None]:
        """
        Validate the input data. Override this method in subclasses for custom validation.

        Args:
            input_data: The input data to validate

        Returns:
            UseCaseResult indicating validation success or failure
        """
        if input_data is None:
            return UseCaseResult.validation_error(
                "input_data", "Input data cannot be None"
            )
        return UseCaseResult.success_result(None)

    async def _execute_with_validation(
        self, input_data: InputType
    ) -> UseCaseResult[OutputType]:
        """
        Execute the use case with input validation.

        Args:
            input_data: The input data for the use case

        Returns:
            UseCaseResult containing the execution result
        """
        # Validate input
        validation_result = self.validate_input(input_data)
        if validation_result.is_error():
            error_msg = validation_result.get_error() or "Validation failed"
            return UseCaseResult.error_result(
                error_msg,
                validation_result.get_exception(),
                validation_result.get_error_code(),
            )

        # Execute the use case
        try:
            return await self.execute(input_data)
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error in use case: {str(e)}", "INTERNAL_ERROR"
            )

    def _return_exception(self, process: UseCaseResult):
        get_exception = process.get_exception()
        get_error_message = process.get_error()
        return UseCaseResult.error_result(get_error_message or "", get_exception)
