import os
from typing import List

import chromadb
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.core.exceptions import (
    AddDocumentCollectionException,
    AddDocumentsException,
    ChromaInitializationException,
    DeleteDocumentException,
    DocumentLoadException,
    DocumentNotFoundException,
    EmbeddingInitializationException,
    ListDocumentsException,
    QAQueryException,
    RetrieverException,
    SimilaritySearchException,
    UnsupportedFileTypeException,
)
from src.core.utils.logger import get_logger

load_dotenv()


class RAGSystem:
    def __init__(self, chroma_directiory: str) -> None:
        try:
            self.client = chromadb.PersistentClient(chroma_directiory)
        except Exception as e:
            # logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise ChromaInitializationException(
                "Failed to initialize ChromaDB client or collection"
            ) from e

        self.logger = get_logger(__name__)
        try:
            self.embedding = OpenAIEmbeddings()
            self.llm = OpenAI(temperature=0.7)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )
        except Exception as e:
            # logger.error(f"Failed to initialize embeddings or LLM: {e}")
            raise EmbeddingInitializationException(
                "Failed to initialize embeddings or LLM"
            ) from e

    def collection(self, collection_name: str):
        try:
            return self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            # logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise ChromaInitializationException(
                "Failed to initialize ChromaDB client or collection"
            ) from e

    def list_documents(self, collection_name: str) -> List[str]:
        """
        Ambil daftar doc_id unik yang ada di collection
        """
        try:
            # ambil semua data dari collection
            all_data = self.collection(collection_name).get(include=["metadatas"])

            # extract doc_id dari metadata
            doc_ids = {
                meta["doc_id"] for meta in all_data["metadatas"] if "doc_id" in meta
            }

            return list(doc_ids)
        except Exception as e:
            # logger.error(f"Error listing documents: {e}")
            raise ListDocumentsException("Failed to list documents") from e

    def load_single_document(
        self,
        directory_path: str,
        file_name: str,
        file_type: str,
    ) -> List[Document]:
        """
        Load a single document from the specified directory.

        Args:
            directory_path: Path to the directory containing the document
            file_name: Name of the file to load
            file_type: Type of the file ('txt' or 'pdf')

        Returns:
            List[Document]: List of loaded documents

        Raises:
            HTTPException: If file type is not supported or loading fails
        """
        try:
            # Validate file type
            if file_type not in ["txt", "pdf"]:
                raise UnsupportedFileTypeException(file_type)

            # Create appropriate loader based on file type
            if file_type == "txt":
                loader = DirectoryLoader(
                    directory_path, glob=f"{file_name}", loader_cls=TextLoader
                )
            elif file_type == "pdf":
                loader = DirectoryLoader(
                    directory_path, glob=f"{file_name}", loader_cls=PyPDFLoader
                )

            # Load documents
            documents: List[Document] = loader.load()

            if not documents:
                raise DocumentNotFoundException(file_name)

            self.logger.info(f"Successfully loaded document: {file_name}")
            return documents

        except (UnsupportedFileTypeException, DocumentNotFoundException):
            # Re-raise known exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error loading document '{file_name}': {str(e)}")
            raise DocumentLoadException(
                f"Failed to load document '{file_name}': {str(e)}"
            ) from e

    def add_documents(
        self, documents: List[Document], doc_id: str, chunk: bool = True
    ) -> List[str]:
        """
        Tambahkan dokumen ke ChromaDB.
        - doc_id: id unik dokumen induk
        - chunk: kalau True dokumen dipotong, kalau False simpan utuh
        Return: list of chunk_ids
        """
        try:
            if not documents:
                # logger.warning(f"Document not found: document_id {doc_id}")
                raise DocumentNotFoundException("")

            if chunk:
                splits = self.text_splitter.split_documents(documents)
            else:
                splits = documents

            texts = [doc.page_content for doc in splits]
            embeddings = self.embedding.embed_documents(texts)

            # Buat ID unik per chunk
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(splits))]

            # Tambahkan ke Chroma dengan metadata doc_id induk
            self.collection.add(
                ids=chunk_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=[{**doc.metadata, "doc_id": doc_id} for doc in splits],
            )
            # logger.info(f"Add document is successfully: document ID {doc_id}")
            return chunk_ids

        except Exception as e:
            # logger.error(f"Error adding documents: {e}")
            raise AddDocumentsException("Failed to add documents") from e
