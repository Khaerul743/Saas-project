# import os
# from typing import Any, List, Optional

# from dotenv import load_dotenv
# from fastapi import HTTPException, status
# from langchain.chains import RetrievalQA
# from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.llms import OpenAI
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import Chroma

# load_dotenv()


# class RAGSystem:
#     def __init__(self, chroma_directiory: str, collection_name: str):
#         self.chroma_directory = chroma_directiory
#         self.collection_name = collection_name
#         self.embeddings = OpenAIEmbeddings()
#         self.llm = OpenAI(temperature=0.7)
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000, chunk_overlap=200, length_function=len
#         )
#         self.vectorstore = None
#         self.qa_chain = None

#         self._setup_chroma()

#     def _setup_chroma(self):
#         try:
#             self.vectorstore = Chroma(
#                 persist_directory=self.chroma_directory,
#                 embedding_function=self.embeddings,
#                 collection_name=self.collection_name,
#             )
#             print(f"Berhasil memuat ChromaDB dari {self.chroma_directory}")
#         except Exception as e:
#             print(f"Membuat ChromaDB baru: {e}")
#             # Buat directory jika belum ada
#             os.makedirs(self.chroma_directory, exist_ok=True)

#     def load_one_document(self, directory_path: str, file_name: str, file_type: str):
#         documents = []
#         if file_type == "txt":
#             loader = DirectoryLoader(
#                 directory_path, glob=f"{file_name}", loader_cls=TextLoader
#             )
#         elif file_type == "pdf":
#             loader = DirectoryLoader(
#                 directory_path, glob=f"{file_name}", loader_cls=PyPDFLoader
#             )

#         try:
#             document = loader.load()
#             documents.extend(document)
#             print(f"Berhasil memuat {len(document)} dokumen {file_type}")
#         except Exception as e:
#             print(f"Error loading {file_type} files: {e}")

#         return documents

#     def load_document(self, directory_path: str, file_types: Optional[List] = None):
#         if file_types is None:
#             file_types = ["pdf", "txt"]

#         documents = []

#         for file_type in file_types:
#             if file_type == "txt":
#                 loader = DirectoryLoader(
#                     directory_path, glob=f"**/*.{file_type}", loader_cls=TextLoader
#                 )
#             elif file_type == "pdf":
#                 loader = DirectoryLoader(
#                     directory_path, glob=f"**/*.{file_type}", loader_cls=PyPDFLoader
#                 )
#             else:
#                 continue
#             try:
#                 document = loader.load()
#                 documents.extend(document)
#                 print(f"Berhasil memuat {len(document)} dokumen {file_type}")
#             except Exception as e:
#                 print(f"Error loading {file_type} files: {e}")

#         return documents

#     def add_document(self, documents: List[Document]):
#         if not documents:
#             print("Tidak ada document yang akan ditambahkan")
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No documents will be added",
#             )

#         texts = self.text_splitter.split_documents(documents)
#         print(f"Dokumen dipecah menjadi {len(texts)} chunks")

#         if self.vectorstore is None:
#             # Buat vector store baru
#             self.vectorstore = Chroma.from_documents(
#                 documents=texts,
#                 embedding=self.embeddings,
#                 persist_directory=self.chroma_directory,
#                 collection_name=self.collection_name,
#             )
#         else:
#             # Tambahkan ke vector store yang sudah ada
#             self.vectorstore.add_documents(texts)

#         self.vectorstore.persist()
#         print(f"Berhasil menambahkan {len(texts)} chunks ke vector store")

#         # Update QA chain
#         self._setup_qa_chain()

#     def _setup_qa_chain(self):
#         if self.vectorstore is None:
#             print("Vector store belum diinisialisasi")
#             return

#         # Buat retriever
#         retriever = self.vectorstore.as_retriever(
#             search_type="similarity",
#             search_kwargs={"k": 4},  # Ambil 4 dokumen paling relevan
#         )

#         # Buat QA chain
#         self.qa_chain = RetrievalQA.from_chain_type(
#             llm=self.llm,
#             chain_type="stuff",
#             retriever=retriever,
#             return_source_documents=True,
#             verbose=True,
#         )

#         print("QA chain berhasil disetup")

#     # ...existing code...

#     def delete_collection(self):
#         """
#         Menghapus seluruh collection ChromaDB yang aktif pada RAGSystem.
#         """
#         if self.vectorstore is not None:
#             try:
#                 self.vectorstore.delete_collection()
#                 print(
#                     f"Collection '{self.collection_name}' berhasil dihapus dari {self.chroma_directory}"
#                 )
#                 self.vectorstore = None
#                 self.qa_chain = None
#             except Exception as e:
#                 print(f"Error saat menghapus collection: {e}")
#         else:
#             print(
#                 "Vectorstore belum diinisialisasi, tidak ada collection yang dihapus."
#             )

#     def query(self, question: str):
#         if self.qa_chain is None:
#             return False

#         try:
#             result = self.qa_chain({"query": question})
#             return {
#                 "answer": result["result"],
#                 "source_documents": result["source_documents"],
#             }
#         except Exception as e:
#             print(f"error saat query ke dokumen: {e}")
#             return False

#     def similarity_search(self, query: str, k: int = 4) -> List[Document]:
#         if self.vectorstore is None:
#             return []
#         return self.vectorstore.similarity_search(query, k=k)


# if __name__ == "__main__":
#     rag = RAGSystem("data", collection_name="my_collections")
#     # documents = rag.load_document("docs", file_types=["pdf"])
#     # rag.add_document(documents)
#     similarity = rag.similarity_search("RPL")
#     print(similarity)
#     # doc = rag.load_one_document("docs", "TUGAS BESAR 2 RPL.pdf", "pdf")
#     # docs = "".join([item.page_content for item in doc])
#     # print(docs)

import logging
import os
import uuid
from typing import List

import chromadb
from dotenv import load_dotenv
from fastapi import HTTPException, status
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


# ...existing code...


class RAGSystem:
    def __init__(self, chroma_directiory: str, collection_name: str):
        try:
            self.client = chromadb.PersistentClient(chroma_directiory)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            # logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

        try:
            self.embedding = OpenAIEmbeddings()
            self.llm = OpenAI(temperature=0.7)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )
        except Exception as e:
            # logger.error(f"Failed to initialize embeddings or LLM: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

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
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_type}. Only 'txt' and 'pdf' are supported.",
                )

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
                raise HTTPException(
                    status_code=404,
                    detail=f"Document '{file_name}' not found or could not be loaded.",
                )

            logger.info(f"Successfully loaded document: {file_name}")
            return documents

        except HTTPException:
            # Re-raise HTTP exceptions as they are already properly formatted
            raise
        except Exception as e:
            logger.error(f"Error loading document '{file_name}': {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load document '{file_name}': {str(e)}",
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

    def list_documents(self) -> List[str]:
        """
        Ambil daftar doc_id unik yang ada di collection
        """
        try:
            # ambil semua data dari collection
            all_data = self.collection.get(include=["metadatas"])

            # extract doc_id dari metadata
            doc_ids = {
                meta["doc_id"] for meta in all_data["metadatas"] if "doc_id" in meta
            }

            return list(doc_ids)
        except Exception as e:
            # logger.error(f"Error listing documents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
                )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again",
            )

    def delete_document(self, doc_id: str):
        """
        Hapus semua chunk berdasarkan doc_id induk
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
            # logger.info(f"Semua chunk dokumen dengan id {doc_id} berhasil dihapus")
            return {"result": f"Delete document is successfully: document ID {doc_id}"}
        except Exception as e:
            # logger.error(f"Error deleting document {doc_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error, please try again later",
            )

    def get_retriever(self):
        try:
            from langchain.vectorstores import Chroma

            vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection.name,
                embedding_function=self.embedding,
            )
            return vectorstore.as_retriever()
        except Exception as e:
            # logger.error(f"Error getting retriever: {e}")
            raise RuntimeError("Gagal mengambil retriever") from e

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
            return False

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
            results = self.collection.query(
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
            raise RuntimeError("Gagal melakukan similarity search di ChromaDB") from e


if __name__ == "__main__":
    rag = RAGSystem("data", "my_collections")

    # docs = rag.load_single_document("documents", "kontol.pdf", "pdf")
    # print(docs)
    # rag.add_documents(docs, "2")
    # print(rag.ask("neraca"))
