import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from fastapi import UploadFile

from src.core.utils.logger import get_logger


@dataclass
class ConvertHexOutput:
    filename: str
    content_type: str
    content: str
    size: int


class SaveFileHandler:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    async def convert_to_hex(self, file: UploadFile) -> ConvertHexOutput:
        # Read file content
        file_content = await file.read()
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError("File too large")
        # file_data = {
        #     "filename": file.filename,
        #     "content_type": file.content_type,
        #     "content": file_content.hex(),  # Convert binary to hex string
        #     "size": len(file_content),
        # }
        file_data = ConvertHexOutput(
            filename=file.filename,
            content_type=file.content_type,
            content=file_content.hex(),
            size=len(file_content),
        )

        # Reset file pointer
        await file.seek(0)

        return file_data

    def create_agent_directory(self, user_id: int, agent_id: str) -> str:
        """
        Create directory for agent documents

        Args:
            user_id: ID of the user
            agent_id: ID of the agent

        Returns:
            str: Path to the created directory
        """
        directory_path = f"documents/user_{user_id}/agent_{agent_id}"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        self.logger.info(f"Created directory: {directory_path}")
        return directory_path

    def save_uploaded_file(
        self, file_data: ConvertHexOutput, directory_path: str
    ) -> Tuple[str, str]:
        """
        Save uploaded file to directory

        Args:
            file_data: File data dictionary containing filename, content, content_type
            directory_path: Directory to save the file

        Returns:
            Tuple[str, str]: (file_path, content_type)

        Raises:
            Exception: If file saving fails
        """
        try:
            # Create file path
            file_path = os.path.join(directory_path, file_data.filename)

            # Write file content from hex string
            file_content = bytes.fromhex(file_data.content)
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Determine content type based on file extension and MIME type
            filename = file_data.filename.lower()
            mime_type = file_data.content_type.lower()

            if filename.endswith(".pdf") or mime_type == "application/pdf":
                content_type = "pdf"
            elif filename.endswith(".csv") or mime_type == "text/csv":
                content_type = "csv"
            elif filename.endswith((".xlsx", ".xls")) or mime_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
            ]:
                content_type = "excel"
            elif filename.endswith(".txt") or mime_type == "text/plain":
                content_type = "txt"
            else:
                # Default to txt for unknown types
                content_type = "txt"

            self.logger.info(f"Saved file: {file_path} (type: {content_type})")
            return file_path, content_type

        except Exception as e:
            self.logger.error(f"Failed to save file {file_data.filename}: {e}")
            raise e

    def cleanup_file_on_error(self, file_path: str) -> None:
        """
        Remove file if it exists (for rollback purposes)

        Args:
            file_path: Path to the file to remove
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Rollback: Removed file {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to remove file {file_path} during rollback: {e}")
