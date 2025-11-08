from dataclasses import dataclass

from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import IMetadata


@dataclass
class CreateMetadataInput:
    history_message_id: int
    total_tokens: int | float
    response_time: float
    model: str
    is_success: bool = True


@dataclass
class CreateMetadataOutput:
    metadata_id: int


class CreateMetadata(BaseUseCase[CreateMetadataInput, CreateMetadataOutput]):
    def __init__(self, metadata_repository: IMetadata):
        self.metadata_repository = metadata_repository

    async def execute(
        self, input_data: CreateMetadataInput
    ) -> UseCaseResult[CreateMetadataOutput]:
        try:
            new_metadata = await self.metadata_repository.create_message_metadata(
                input_data.history_message_id,
                input_data.total_tokens,
                input_data.response_time,
                input_data.model,
                input_data.is_success,
            )

            return UseCaseResult.success_result(CreateMetadataOutput(new_metadata.id))
        except Exception as e:
            return UseCaseResult.error_result(
                f"Something wrong at create message metadata: {str(e)}", e
            )
