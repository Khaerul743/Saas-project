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

load_dotenv()


# ...existing code...


class RAGSystem:
    def __init__(self, chroma_directiory: str, collection_name: str):
        try:
            self.client = chromadb.PersistentClient(chroma_directiory)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client or collection: {e}")
            raise RuntimeError("Gagal inisialisasi ChromaDB") from e

        try:
            self.embedding = OpenAIEmbeddings()
            self.llm = OpenAI(temperature=0.7)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )
        except Exception as e:
            logging.error(f"Failed to initialize embeddings or LLM: {e}")
            raise RuntimeError("Gagal inisialisasi Embeddings/LLM") from e

    def load_single_document(
        self, directory_path: str, file_name: str, file_type: str
    ) -> List[Document]:
        try:
            if file_type == "txt":
                loader = DirectoryLoader(
                    directory_path, glob=f"{file_name}", loader_cls=TextLoader
                )
            elif file_type == "pdf":
                loader = DirectoryLoader(
                    directory_path, glob=f"{file_name}", loader_cls=PyPDFLoader
                )
            else:
                raise ValueError("File type must be 'txt' or 'pdf'")
            documents: List[Document] = loader.load()
            return documents
        except Exception as e:
            logging.error(f"Error loading document '{file_name}': {e}")
            raise RuntimeError(f"Gagal memuat dokumen {file_name}") from e

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
            raise RuntimeError(f"Gagal memuat dokumen dari folder {directory}") from e

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
            logging.error(f"Error listing documents: {e}")
            raise RuntimeError("Gagal mengambil daftar dokumen dari ChromaDB") from e

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
                raise ValueError("Dokumen kosong tidak dapat ditambahkan")

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

            return chunk_ids

        except Exception as e:
            logging.error(f"Error adding documents: {e}")
            raise RuntimeError("Gagal menambahkan dokumen ke ChromaDB") from e

    def delete_document(self, doc_id: str) -> None:
        """
        Hapus semua chunk berdasarkan doc_id induk
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
            logging.info(f"Semua chunk dokumen dengan id {doc_id} berhasil dihapus")
        except Exception as e:
            logging.error(f"Error deleting document {doc_id}: {e}")
            raise RuntimeError("Gagal menghapus dokumen dari ChromaDB") from e

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
            logging.error(f"Error getting retriever: {e}")
            raise RuntimeError("Gagal mengambil retriever") from e

    def ask(self, query: str) -> str:
        try:
            retriever = self.get_retriever()
            qa = RetrievalQA.from_chain_type(
                llm=self.llm, retriever=retriever, return_source_documents=True
            )
            result = qa({"query": query})
            return result["result"]
        except Exception as e:
            logging.error(f"Error during QA query: {e}")
            raise RuntimeError("Gagal melakukan query ke dokumen") from e

    def similarity_search(self, query: str, k: int = 4) -> str:
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
            logging.error(f"Error performing similarity search: {e}")
            raise RuntimeError("Gagal melakukan similarity search di ChromaDB") from e


if __name__ == "__main__":
    rag = RAGSystem("chroma_db", "agent_2")
    print(rag.list_documents())
