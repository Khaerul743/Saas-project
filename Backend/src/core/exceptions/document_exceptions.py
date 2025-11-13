from fastapi import status

from src.core.exceptions import BaseCustomeException


class FileTooLargeException(BaseCustomeException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": "File too large, max size is 10 MB",
            },
        )


class DocumentNotFound(BaseCustomeException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "DOCUMENT_NOT_FOUND",
                "message": "Document not found, please enter the correct id",
                "document_id": document_id,
            },
        )
