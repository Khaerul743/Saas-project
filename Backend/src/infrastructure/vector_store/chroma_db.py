import logging
import os
import uuid
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

logger = get_logger(__name__)

load_dotenv()


# ...existing code...


class RAGSystem:
    def __init__(self, chroma_directiory: str):
        try:
            self.client = chromadb.PersistentClient(chroma_directiory)
            self.collection_name = None
        except Exception as e:
            # logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise ChromaInitializationException(
                "Failed to initialize ChromaDB client or collection"
            ) from e

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

    def initial_collection(self, collection_name: str):
        self.collection_name = collection_name

    def collection(self):
        try:
            if not self.collection_name:
                raise ChromaInitializationException("Please initial collection first")
            return self.client.get_or_create_collection(name=self.collection_name)
        except Exception as e:
            # logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise ChromaInitializationException(
                "Failed to initialize ChromaDB client or collection"
            ) from e

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

            logger.info(f"Successfully loaded document: {file_name}")
            return documents

        except (UnsupportedFileTypeException, DocumentNotFoundException):
            # Re-raise known exceptions
            raise
        except Exception as e:
            logger.error(f"Error loading document '{file_name}': {str(e)}")
            raise DocumentLoadException(
                f"Failed to load document '{file_name}': {str(e)}"
            ) from e

    def load_documents(self, directory: str) -> List[Document]:
        try:
            loaders = [
                DirectoryLoader(directory, glob="*.pdf", loader_cls=PyPDFLoader),
                DirectoryLoader(directory, glob="*.txt", loader_cls=TextLoader),
            ]
            documents: List[Document] = []
            for loader in loaders:
                documents.extend(loader.load())
            return documents
        except Exception as e:
            logging.error(f"Error loading documents from '{directory}': {e}")
            raise DocumentLoadException(
                "Failed to load documents from directory"
            ) from e

    def list_documents(self) -> List[str]:
        """
        Ambil daftar doc_id unik yang ada di collection
        """
        try:
            # ambil semua data dari collection
            all_data = self.collection().get(include=["metadatas"])

            # extract doc_id dari metadata
            doc_ids = {
                meta["doc_id"] for meta in all_data["metadatas"] if "doc_id" in meta
            }

            return list(doc_ids)
        except Exception as e:
            # logger.error(f"Error listing documents: {e}")
            raise ListDocumentsException("Failed to list documents") from e

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
            self.collection().add(
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

    def add_document_collection(
        self, directory_path: str, file_name: str, file_type: str, doc_id: str
    ):
        """
        Add a document to the RAG system.

        Args:
            directory_path: Path to the directory containing the document
            file_name: Name of the file to load
            file_type: Type of the file ('txt' or 'pdf')
            doc_id: Unique identifier for the document
        """
        try:
            # Ensure directory exists
            if not os.path.exists(directory_path + "/"):
                os.makedirs(directory_path, exist_ok=True)

            # Load document using RAG system
            documents = self.load_single_document(directory_path, file_name, file_type)

            # Add documents to the RAG system
            self.add_documents(documents, doc_id)

            logger.info(f"Successfully added document '{file_name}' with ID '{doc_id}'")
        except Exception as e:
            logger.error(f"Failed to add document '{file_name}': {str(e)}")
            raise AddDocumentCollectionException(
                "Failed to add document to collection"
            ) from e

    def delete_document(self, doc_id: str):
        """
        Hapus semua chunk berdasarkan doc_id induk
        """
        try:
            self.collection().delete(where={"doc_id": doc_id})
            # logger.info(f"Semua chunk dokumen dengan id {doc_id} berhasil dihapus")
            return {"result": f"Delete document is successfully: document ID {doc_id}"}
        except Exception as e:
            # logger.error(f"Error deleting document {doc_id}: {e}")
            raise DeleteDocumentException("Failed to delete document") from e

    def get_retriever(self):
        try:
            from langchain.vectorstores import Chroma

            vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection().name,
                embedding_function=self.embedding,
            )
            return vectorstore.as_retriever()
        except Exception as e:
            # logger.error(f"Error getting retriever: {e}")
            raise RetrieverException("Failed to get retriever") from e

    def ask(self, query: str):
        try:
            retriever = self.get_retriever()
            qa = RetrievalQA.from_chain_type(
                llm=self.llm, retriever=retriever, return_source_documents=True
            )
            result = qa({"query": query})
            return result["result"]
        except Exception as e:
            logging.error(f"Error during QA query: {e}")
            raise QAQueryException("Failed during QA query") from e

    def similarity_search(self, query: str, k: int = 5) -> str:
        """
        Melakukan similarity search di ChromaDB berdasarkan query.

        Args:
            query (str): Query teks yang ingin dicari kemiripannya.
            k (int): Jumlah dokumen paling relevan yang diambil.

        Returns:
            str: String hasil pencarian berisi page, source, dan content.
        """
        try:
            # Generate embedding untuk query
            query_embedding = self.embedding.embed_query(query)

            # Query ke collection ChromaDB
            results = self.collection().query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"],
            )

            # Bangun string hasil
            output_lines = []
            for doc, meta in zip(
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
            ):
                page = meta.get("page", "N/A")
                source = meta.get("source", "N/A")
                output_lines.append(f"[Page: {page} | Source: {source}]\n{doc}\n")

            return "\n".join(output_lines).strip()
        except Exception as e:
            # logger.error(f"Error performing similarity search: {e}")
            raise SimilaritySearchException(
                "Failed to perform similarity search in ChromaDB"
            ) from e


if __name__ == "__main__":
    rag = RAGSystem("data", "my_collections")

    # docs = rag.load_single_document("documents", "kontol.pdf", "pdf")
    # print(docs)
    # rag.add_documents(docs, "2")
    # print(rag.ask("neraca"))
