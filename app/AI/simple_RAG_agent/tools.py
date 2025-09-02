from app.RAG import RAGSystem


class AgentTools:
    def __init__(self, chromadb_path: str, collection_name: str):
        self.chromadb_path = chromadb_path
        self.collection_name = collection_name
        self.rag = RAGSystem(self.chromadb_path, self.collection_name)

    def get_document(self, query: str):
        """Gunakan tool untuk mencari informasi dokumen yang telah diberikan oleh pengguna."""
        try:
            get_document = self.rag.query(query)
            if not get_document:
                list_docs = []
                documents = self.rag.similarity_search(query)
                for document in documents:
                    detail_doc = {
                        "source": document.metadata["source"],
                        "page": document.metadata["page"],
                        "content": document.page_content,
                    }
                    list_docs.append(detail_doc)

                get_document = "Berikut adalah hasil search dari document:"
                for item in list_docs:
                    get_document += f"\n**PAGE {item['page']}**\n- source: {item['source']}\n-content: {item['content']}\n"

                print(get_document)
            return get_document
        except Exception as e:
            print(f"Terjadi kesalahan di tool get_document: {e}")
            return f"Terjadi kesalahan saat query ke document {e}"


if __name__ == "__main__":
    tool = AgentTools()
    tool_result = tool.get_document("Apa itu RPL?")
    print(tool_result)
