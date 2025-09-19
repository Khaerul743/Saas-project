from app.AI.document_store.RAG import RAGSystem

class AgentTools:
    def __init__(self, chromadb_path: str, collection_name: str):
        self.chromadb_path = chromadb_path
        self.collection_name = collection_name
        self.rag = RAGSystem(self.chromadb_path, self.collection_name)

    def get_document(self, query: str):
        """Gunakan tool untuk mencari informasi FAQ yang telah diberikan oleh pengguna."""
        print("agent menggunakan tool get_document")
        try:
            get_document = self.rag.ask(query)
            if not get_document:
                get_document = self.rag.similarity_search(query)

                print(get_document)
            return get_document
        except Exception as e:
            print(f"Terjadi kesalahan di tool get_document: {e}")
            return f"Terjadi kesalahan saat query ke document {e}"