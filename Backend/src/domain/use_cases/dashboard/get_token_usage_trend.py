from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal

from src.core.exceptions.auth_exceptions import ValidationException
from src.core.exceptions.user_exceptions import UserNotFoundException
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IMetadata, UserRepositoryInterface


@dataclass
class GetTokenUsageTrendInput:
    user_id: int
    start_date: datetime
    end_date: datetime
    group_by: Literal["day", "week", "month"]


@dataclass
class TokenUsageTrendItem:
    period: str
    total_tokens: int


@dataclass
class GetTokenUsageTrendOutput:
    trend: List[TokenUsageTrendItem]


class GetTokenUsageTrend(BaseUseCase[GetTokenUsageTrendInput, GetTokenUsageTrendOutput]):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        metadata_repository: IMetadata,
    ):
        self.user_repository = user_repository
        self.metadata_repository = metadata_repository

    def _format_token_usage_trend_data(self, results: List) -> List[TokenUsageTrendItem]:
        """
        Format token usage trend data from database query results.

        Args:
            results: Raw query results from database

        Returns:
            List of TokenUsageTrendItem containing period and total_tokens
        """
        trend = []
        for r in results:
            period = r.period
            period_str = period.isoformat() if hasattr(period, "isoformat") else str(period)

            trend.append(
                TokenUsageTrendItem(period=period_str, total_tokens=int(r.total_tokens or 0))
            )

        return trend

    async def execute(
        self, input_data: GetTokenUsageTrendInput
    ) -> UseCaseResult[GetTokenUsageTrendOutput]:
        try:
            # Validate user exists
            user = await self.user_repository.get_user_by_id(input_data.user_id)
            if not user:
                return UseCaseResult.error_result(
                    "User not found",
                    UserNotFoundException(input_data.user_id),
                    "USER_NOT_FOUND",
                )

            # Validate group_by
            if input_data.group_by not in ["day", "week", "month"]:
                return UseCaseResult.error_result(
                    "Invalid group_by value. Use day|week|month",
                    ValidationException("group_by", "Invalid group_by value"),
                    "INVALID_GROUP_BY",
                )

            # Validate date range
            if input_data.start_date > input_data.end_date:
                return UseCaseResult.error_result(
                    "Start date must be before end date",
                    ValidationException("date_range", "Start date must be before end date"),
                    "INVALID_DATE_RANGE",
                )

            # Get token usage trend from repository
            results = await self.metadata_repository.get_token_usage_trend(
                user_id=input_data.user_id,
                start_date=input_data.start_date,
                end_date=input_data.end_date,
                group_by=input_data.group_by,
            )

            # Format results
            trend = self._format_token_usage_trend_data(list(results))

            return UseCaseResult.success_result(GetTokenUsageTrendOutput(trend=trend))

        except ValueError as e:
            return UseCaseResult.error_result(
                str(e), ValidationException("group_by", str(e)), "INVALID_GROUP_BY"
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting token usage trend: {str(e)}", e
            )

