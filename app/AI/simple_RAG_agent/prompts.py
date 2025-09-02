from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from app.memory import MemoryControl

load_dotenv()


class AgentPromptControl:
    def __init__(
        self,
        is_include_memory: bool = False,
        memory_provider: Optional[str] = "",
        provider_host: Optional[str] = "",
        provider_port: Optional[str] = "",
        memory_id: Optional[str] = "default",
    ):
        self.is_include_memory = is_include_memory
        if self.is_include_memory:
            self.memory = MemoryControl(
                memory_provider=memory_provider,
                provider_host=provider_host,
                provider_port=provider_port,
            )
            self.memory_id = memory_id

    def main_agent(self, user_message: str):
        previous_context = "tidak ada."
        if self.is_include_memory:
            previous_context = self.memory.get_context(
                query=user_message, memory_id=self.memory_id
            )
            print(f"===========PREVIOUS CONTEXT=============\n{previous_context}")
        return [
            SystemMessage(
                content=f"""
Kamu adalah asisten pribadi.
Pastikan kamu mengingat state history messages sebelumnya sebelum menggunakan tool.
Kamu memiliki akses ke tool berikut:
- get_document(query: str): Gunakan untuk mengambil informasi dari dokumen pengguna.

Instruksi:
1. Jika kamu tidak tahu jawabannya atau perlu informasi dari dokumen, PANGGIL tool get_document.
2. Jangan jawab "tidak tahu" tanpa mencoba tool.
3. Selalu prioritaskan penggunaan tool sebelum menebak.

Perlu diingat bahwa jangan terlalu mengandalkan tool untuk menjawab, melainkan kamu bisa menggukanan state messages history untuk menjawab pertanyaan.
Gunakan tool seperlunya saja.

percakapan sebelumnya:
{previous_context}
"""
            ),
            HumanMessage(content=user_message),
        ]

    def agent_describe_document(self, user_message: str, document: str):
        return [
            SystemMessage(
                content="""
Kamu adalah agent yang bertugas untuk mendeskripsikan document yang telah diberikan oleh pengguna.
Instruksi:
1. Deskripsikan document dari pengguna dengan jelas dan singkat.
2. Pastikan deskripsi tersebut sesuai dengan instruksi pengguna(jika ada).
"""
            ),
            HumanMessage(
                content=f"""
instruksi:{user_message}
Berikut adalah isi dokumen yang harus kamu deskripsikan:
{document}
"""
            ),
        ]

    def agent_answer_rag_question(self, user_message: str, tool_message: str):
        return [
            SystemMessage(
                content=f"""
Kamu adalah agent yang bertugas untuk menjelaskan hasil pencarian dari agent sebelumnya mengenai document RAG.
Berikut adalah hasil pencarian document RAG:
{tool_message}
Pastikan kamu menjawab pertanyaan pengguna berdasarkan hasil pencarian document tersebut.

"""
            ),
            HumanMessage(content=user_message),
        ]


if __name__ == "__main__":
    prompt = AgentPromptControl(is_include_memory=False)
    print(prompt.main_agent(user_message="siapakah nama saya?"))
