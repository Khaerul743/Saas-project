import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

load_dotenv()


class RAGSystem:
    def __init__(self, chroma_directiory: str, collection_name: str):
        self.chroma_directory = chroma_directiory
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.7)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, length_function=len
        )
        self.vectorstore = None
        self.qa_chain = None

        self._setup_chroma()

    def _setup_chroma(self):
        try:
            self.vectorstore = Chroma(
                persist_directory=self.chroma_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
            )
            print(f"Berhasil memuat ChromaDB dari {self.chroma_directory}")
        except Exception as e:
            print(f"Membuat ChromaDB baru: {e}")
            # Buat directory jika belum ada
            os.makedirs(self.chroma_directory, exist_ok=True)

    def load_one_document(self, directory_path: str, file_name: str, file_type: str):
        documents = []
        if file_type == "txt":
            loader = DirectoryLoader(
                directory_path, glob=f"{file_name}", loader_cls=TextLoader
            )
        elif file_type == "pdf":
            loader = DirectoryLoader(
                directory_path, glob=f"{file_name}", loader_cls=PyPDFLoader
            )

        try:
            document = loader.load()
            documents.extend(document)
            print(f"Berhasil memuat {len(document)} dokumen {file_type}")
        except Exception as e:
            print(f"Error loading {file_type} files: {e}")

        return documents

    def load_document(self, directory_path: str, file_types: Optional[List] = None):
        if file_types is None:
            file_types = ["pdf", "txt"]

        documents = []

        for file_type in file_types:
            if file_type == "txt":
                loader = DirectoryLoader(
                    directory_path, glob=f"**/*.{file_type}", loader_cls=TextLoader
                )
            elif file_type == "pdf":
                loader = DirectoryLoader(
                    directory_path, glob=f"**/*.{file_type}", loader_cls=PyPDFLoader
                )
            else:
                continue
            try:
                document = loader.load()
                documents.extend(document)
                print(f"Berhasil memuat {len(document)} dokumen {file_type}")
            except Exception as e:
                print(f"Error loading {file_type} files: {e}")

        return documents

    def add_document(self, documents: List[Document]):
        if not documents:
            print("Tidak ada document yang akan ditambahkan")
            return

        texts = self.text_splitter.split_documents(documents)
        print(f"Dokumen dipecah menjadi {len(texts)} chunks")

        if self.vectorstore is None:
            # Buat vector store baru
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=self.chroma_directory,
                collection_name=self.collection_name,
            )
        else:
            # Tambahkan ke vector store yang sudah ada
            self.vectorstore.add_documents(texts)

        self.vectorstore.persist()
        print(f"Berhasil menambahkan {len(texts)} chunks ke vector store")

        # Update QA chain
        self._setup_qa_chain()

    def _setup_qa_chain(self):
        if self.vectorstore is None:
            print("Vector store belum diinisialisasi")
            return

        # Buat retriever
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},  # Ambil 4 dokumen paling relevan
        )

        # Buat QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=True,
        )

        print("QA chain berhasil disetup")

    def query(self, question: str):
        if self.qa_chain is None:
            return False

        try:
            result = self.qa_chain({"query": question})
            return {
                "answer": result["result"],
                "source_documents": result["source_documents"],
            }
        except Exception as e:
            print(f"error saat query ke dokumen: {e}")
            return False

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)


if __name__ == "__main__":
    rag = RAGSystem("data", collection_name="my_collections")
    # documents = rag.load_document("docs", file_types=["pdf"])
    # rag.add_document(documents)
    similarity = rag.similarity_search("RPL")
    print(similarity)
    # doc = rag.load_one_document("docs", "TUGAS BESAR 2 RPL.pdf", "pdf")
    # docs = "".join([item.page_content for item in doc])
    # print(docs)
