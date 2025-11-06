from typing import Literal, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from app.AI.utils.tone import get_tone

load_dotenv()


class SimpleRagPrompt:
    def __init__(
        self,
        tone: Literal["friendly", "formal", "casual", "profesional"],
        base_prompt: Optional[str] = None,
    ):
        self.base_prompt = base_prompt
        self.tone = tone

    def main_agent(self, user_message: str, previous_context: Optional[str] = None):
        # Get tone-based personality and communication style
        tone_prompt = get_tone(self.tone)
        return [
            SystemMessage(
                content=f"""
Kamu adalah AI Assistant yang memiliki kepribadian dan gaya komunikasi tertentu.

BASE PROMPT (Tugas Utama):
{self.base_prompt}

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
{previous_context if previous_context else "Belum ada percakapan sebelumnya"}

Sekarang, jawablah pertanyaan pengguna dengan konsisten mengikuti kepribadian dan gaya komunikasi yang telah ditentukan.
"""
            ),
            HumanMessage(content=user_message),
        ]

    def agent_describe_document(self, user_message: str, document: str):
        tone_prompt = get_tone(self.tone)
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

    def agent_answer_rag_question(self, user_message: str, tool_message):
        tone_prompt = get_tone(self.tone)
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


# if __name__ == "__main__":
#     prompt = AgentPromptControl(is_include_memory=False)
#     print(
#         prompt.main_agent(
#             user_message="siapakah nama saya?",
#             base_prompt="Kamu adalah asisten yang membantu pengguna",
#             tone="friendly",
#         )
#     )
