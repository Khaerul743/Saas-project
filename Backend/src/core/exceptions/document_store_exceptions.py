from typing import Optional

from fastapi import status

from src.core.exceptions import BaseCustomeException


class DocumentStoreException(BaseCustomeException):
    """Base HTTP exception for document store related errors."""


class ChromaInitializationException(DocumentStoreException):
    def __init__(
        self, message: str = "Failed to initialize ChromaDB client or collection"
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CHROMA_INIT_FAILED",
                "message": message,
            },
        )


class EmbeddingInitializationException(DocumentStoreException):
    def __init__(self, message: str = "Failed to initialize embeddings or LLM"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "EMBEDDING_INIT_FAILED",
                "message": message,
            },
        )


class UnsupportedFileTypeException(DocumentStoreException):
    def __init__(self, file_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "UNSUPPORTED_FILE_TYPE",
                "message": f"Unsupported file type: {file_type}. Only 'txt' and 'pdf' are supported.",
                "field": "file_type",
                "value": file_type,
            },
        )


class DocumentLoadException(DocumentStoreException):
    def __init__(self, message: str = "Failed to load document"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DOCUMENT_LOAD_FAILED",
                "message": message,
            },
        )


class DocumentNotFoundException(DocumentStoreException):
    def __init__(self, file_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "DOCUMENT_NOT_FOUND",
                "message": f"Document '{file_name}' not found or could not be loaded.",
                "field": "file_name",
                "value": file_name,
            },
        )


class ListDocumentsException(DocumentStoreException):
    def __init__(self, message: str = "Failed to list documents"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LIST_DOCUMENTS_FAILED",
                "message": message,
            },
        )


class AddDocumentsException(DocumentStoreException):
    def __init__(self, message: str = "Failed to add documents"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ADD_DOCUMENTS_FAILED",
                "message": message,
            },
        )


class AddDocumentCollectionException(DocumentStoreException):
    def __init__(self, message: str = "Failed to add document to collection"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ADD_DOCUMENT_COLLECTION_FAILED",
                "message": message,
            },
        )


class DeleteDocumentException(DocumentStoreException):
    def __init__(self, message: str = "Failed to delete document"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DELETE_DOCUMENT_FAILED",
                "message": message,
            },
        )


class RetrieverException(DocumentStoreException):
    def __init__(self, message: str = "Failed to get retriever"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "RETRIEVER_FAILED",
                "message": message,
            },
        )


class QAQueryException(DocumentStoreException):
    def __init__(self, message: str = "Failed during QA query"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QA_QUERY_FAILED",
                "message": message,
            },
        )


class SimilaritySearchException(DocumentStoreException):
    def __init__(
        self, message: str = "Failed to perform similarity search in ChromaDB"
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SIMILARITY_SEARCH_FAILED",
                "message": message,
            },
        )


class DirectoryPathNotFound(DocumentStoreException):
    def __init__(self, message: str = "Directory path not found"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DIRECTORY_PATH_NOT_FOUND",
                "message": message,
            },
        )
