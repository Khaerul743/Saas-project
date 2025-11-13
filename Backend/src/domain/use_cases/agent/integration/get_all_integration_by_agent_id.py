from dataclasses import dataclass
from typing import Literal

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IIntergrationRepository


@dataclass
class GetAllIntegrationByAgentIdInput:
    agent_id: str


@dataclass
class IntegrationItem:
    id: int
    agent_id: str
    platform: Literal["api", "telegram", "whatsapp"]
    status: Literal["active", "non-active"]
    api_key: str | None
    created_at: str


@dataclass
class GetAllIntegrationByAgentIdOutput:
    integrations: list[IntegrationItem]


class GetAllIntegrationByAgentId(
    BaseUseCase[GetAllIntegrationByAgentIdInput, GetAllIntegrationByAgentIdOutput]
):
    def __init__(self, integration_repository: IIntergrationRepository):
        self.integration_repository = integration_repository

    async def execute(
        self, input_data: GetAllIntegrationByAgentIdInput
    ) -> UseCaseResult[GetAllIntegrationByAgentIdOutput]:
        try:
            integrations = await self.integration_repository.get_all_by_agent_id(
                input_data.agent_id
            )

            integration_items = []
            for integration in integrations:
                # Get api_key from platform_config if exists
                api_key = None
                if integration.platform_config:
                    api_key = integration.platform_config.api_key  # type: ignore[attr-defined]

                # Format created_at safely
                created_at_str = ""
                if hasattr(integration, "created_at") and integration.created_at:  # type: ignore[attr-defined]
                    created_at_str = integration.created_at.isoformat()  # type: ignore[attr-defined]

                integration_items.append(
                    IntegrationItem(
                        id=integration.id,  # type: ignore[attr-defined]
                        agent_id=integration.agent_id,  # type: ignore[attr-defined]
                        platform=integration.platform,  # type: ignore[assignment]
                        status=integration.status,  # type: ignore[assignment]
                        api_key=api_key,
                        created_at=created_at_str,
                    )
                )

            return UseCaseResult.success_result(
                GetAllIntegrationByAgentIdOutput(integrations=integration_items)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while getting integrations: {str(e)}", e
            )

