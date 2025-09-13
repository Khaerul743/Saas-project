from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from app.AI.memory.memory import MemoryControl
from app.AI.utils.tone import get_tone

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

    def main_agent(self, user_message: str, base_prompt: str, tone: str):
        previous_context = "tidak ada."
        if self.is_include_memory:
            previous_context = self.memory.get_context(
                query=user_message, memory_id=self.memory_id
            )
            print(f"===========PREVIOUS CONTEXT=============\n{previous_context}")
        
        # Get tone-based personality and communication style
        tone_prompt = get_tone(tone)
        
        return [
            SystemMessage(
                content=f"""
Kamu adalah AI Assistant yang memiliki kepribadian dan gaya komunikasi tertentu.

BASE PROMPT (Tugas Utama):
{base_prompt}

KEPRIBADIAN DAN GAYA KOMUNIKASI:
{tone_prompt}

PENTING: Selalu konsisten dengan kepribadian dan gaya komunikasi yang telah ditentukan di atas. 
Jangan pernah mengubah kepribadian atau gaya komunikasi selama percakapan.

FITUR DAN TOOLS:
Kamu memiliki akses ke tool berikut:
- get_document(query: str): Gunakan untuk mengambil informasi dari dokumen pengguna.

INSTRUKSI UTAMA:
1. Jika kamu tidak tahu jawabannya atau perlu informasi dari dokumen, PANGGIL tool get_document.
2. Jangan jawab "tidak tahu" tanpa mencoba tool terlebih dahulu.
3. Selalu prioritaskan penggunaan tool sebelum menebak.
4. Jangan terlalu mengandalkan tool untuk menjawab, gunakan state messages history untuk menjawab pertanyaan.
5. Gunakan tool seperlunya saja.

PERCAKAPAN SEBELUMNYA:
{previous_context}

Sekarang, jawablah pertanyaan pengguna dengan konsisten mengikuti kepribadian dan gaya komunikasi yang telah ditentukan.
"""
            ),
            HumanMessage(content=user_message),
        ]

    def agent_describe_document(self, user_message: str, document: str, tone: str = "formal"):
        tone_prompt = get_tone(tone)
        return [
            SystemMessage(
                content=f"""
Kamu adalah agent yang bertugas untuk mendeskripsikan document yang telah diberikan oleh pengguna.

KEPRIBADIAN DAN GAYA KOMUNIKASI:
{tone_prompt}

PENTING: Selalu konsisten dengan kepribadian dan gaya komunikasi yang telah ditentukan di atas.

INSTRUKSI:
1. Deskripsikan document dari pengguna dengan jelas dan singkat.
2. Pastikan deskripsi tersebut sesuai dengan instruksi pengguna (jika ada).
3. Gunakan gaya komunikasi yang sesuai dengan kepribadian yang ditentukan.
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

    def agent_answer_rag_question(self, user_message: str, tool_message: str, tone: str = "formal"):
        tone_prompt = get_tone(tone)
        return [
            SystemMessage(
                content=f"""
Kamu adalah agent yang bertugas untuk menjelaskan hasil pencarian dari agent sebelumnya mengenai document RAG.

KEPRIBADIAN DAN GAYA KOMUNIKASI:
{tone_prompt}

PENTING: Selalu konsisten dengan kepribadian dan gaya komunikasi yang telah ditentukan di atas.

HASIL PENCARIAN DOCUMENT RAG:
{tool_message}

INSTRUKSI:
1. Pastikan kamu menjawab pertanyaan pengguna berdasarkan hasil pencarian document tersebut.
2. Gunakan gaya komunikasi yang sesuai dengan kepribadian yang ditentukan.
3. Sampaikan informasi dengan cara yang sesuai dengan karakteristik kepribadian.

"""
            ),
            HumanMessage(content=user_message),
        ]


if __name__ == "__main__":
    prompt = AgentPromptControl(is_include_memory=False)
    print(prompt.main_agent(
        user_message="siapakah nama saya?", 
        base_prompt="Kamu adalah asisten yang membantu pengguna", 
        tone="friendly"
    ))
