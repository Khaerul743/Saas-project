from dataclasses import dataclass

from fastapi import UploadFile

from src.core.utils.save_file import SaveFileHandler
from src.domain.use_cases.base import BaseUseCase, UseCaseResult
from src.domain.use_cases.interfaces import DocumentRepositoryInterface


@dataclass
class UploadedDocumentInput:
    user_id: int
    agent_id: str
    file: UploadFile


@dataclass
class UploadedDocumentOutput:
    document_id: int
    agent_id: str
    file_name: str
    content_type: str
    directory_path: str


class UploadedDocumentHandler(
    BaseUseCase[UploadedDocumentInput, UploadedDocumentOutput]
):
    def __init__(
        self,
        document_repository: DocumentRepositoryInterface,
        save_file: SaveFileHandler,
    ):
        self.document_repository = document_repository
        self.save_file = save_file

    async def execute(
        self, input_data: UploadedDocumentInput
    ) -> UseCaseResult[UploadedDocumentOutput]:
        try:
            # Convert to hex
            file_hex = await self.save_file.convert_to_hex(input_data.file)

            # Create folder directory path
            directory_path = self.save_file.create_agent_directory(
                input_data.user_id, input_data.agent_id
            )

            # save file content
            file_path, content_type = self.save_file.save_uploaded_file(
                file_hex, directory_path
            )

            add_document = await self.document_repository.add_document(
                input_data.agent_id,
                input_data.file.filename,
                content_type,
            )

            return UseCaseResult.success_result(
                UploadedDocumentOutput(
                    document_id=add_document.id,
                    agent_id=input_data.agent_id,
                    file_name=add_document.file_name,
                    content_type=content_type,
                    directory_path=directory_path,
                )
            )
        except ValueError as e:
            # self.save_file.cleanup_file_on_error(file_path)
            return UseCaseResult.error_result("File too large", e)

        except Exception as e:
            # self.save_file.cleanup_file_on_error(file_path)
            return UseCaseResult.error_result(
                f"Unexpected error in uploaded document handler: {e}", e
            )
