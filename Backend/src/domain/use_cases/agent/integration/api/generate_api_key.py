import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IApiKeyRepository


@dataclass
class GenerateApiKeyInput:
    user_id: int
    agent_id: str
    expires_at: datetime = datetime.utcnow() + timedelta(days=30)


@dataclass
class GenerateApiKeyOutput:
    api_key_id: int
    api_key: str


class GenerateApiKey(BaseUseCase[GenerateApiKeyInput, GenerateApiKeyOutput]):
    def __init__(self, api_key_repository: IApiKeyRepository):
        self.api_key_repository = api_key_repository

    def generate_api_key(self) -> str:
        # Generate a secure random API key
        alphabet = string.ascii_letters + string.digits
        api_key = "".join(secrets.choice(alphabet) for _ in range(32))
        return api_key

    async def execute(
        self, input_data: GenerateApiKeyInput
    ) -> UseCaseResult[GenerateApiKeyOutput]:
        try:
            api_key = self.generate_api_key()
            new_api_key = await self.api_key_repository.create_api_key(
                input_data.user_id,
                input_data.agent_id,
                api_key,
                input_data.expires_at,
            )

            return UseCaseResult.success_result(
                GenerateApiKeyOutput(new_api_key.id, api_key)
            )
        except Exception as e:
            return UseCaseResult.error_result(
                f"Unexpected error while generate api key: {str(e)}", e
            )
