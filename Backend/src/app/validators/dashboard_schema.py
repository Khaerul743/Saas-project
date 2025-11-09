from pydantic import BaseModel

from src.app.validators.base import BaseSchemaOut


class DashboardOverviewData(BaseModel):
    token_usage: int
    total_conversations: int
    active_agents: int
    average_response_time: float
    success_rate: float


class DashboardOverviewResponse(BaseSchemaOut):
    data: DashboardOverviewData

