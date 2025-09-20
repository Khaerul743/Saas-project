from langchain_core.messages import SystemMessage, HumanMessage
from typing import Optional
from app.AI.memory.memory import MemoryControl
from app.AI.utils.tone import get_tone

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
    def trust_level_check(self, history_messages:str):
        return [
            SystemMessage(content=
"""
Kamu adalah agent yang bertugas untuk mengecek level trust dan emosi pengguna berdasarkan riwayat percakapan.

## TUGAS:
1. Analisis riwayat percakapan untuk mendeteksi emosi dan tingkat kepercayaan
2. Identifikasi apakah pengguna merasa frustrasi, marah, atau tidak percaya
3. Tentukan level trust pengguna terhadap AI/system
4. Berikan rekomendasi untuk meningkatkan kepercayaan pengguna

## INDIKATOR EMOSI NEGATIF:
- Kata-kata kasar atau tidak sopan
- Ekspresi frustrasi ("kenapa sih", "ribet banget", "gak jelas")
- Ketidakpercayaan ("gak percaya", "bohong", "ngapain")
- Kekecewaan ("kecewa", "menyesal", "gak puas")
- Ketidaksabaran ("capek", "bosan", "gak sabar")

## LEVEL TRUST (PERSENTASE):
**80-100% (Trust Tinggi):**
- Pengguna kooperatif dan sopan
- Mengajukan pertanyaan dengan jelas
- Tidak menunjukkan tanda-tanda frustrasi

**50-79% (Trust Sedang):**
- Pengguna netral, tidak menunjukkan emosi khusus
- Pertanyaan biasa tanpa indikasi masalah

**0-49% (Trust Rendah):**
- Pengguna menunjukkan frustrasi atau ketidakpercayaan
- Menggunakan kata-kata kasar atau tidak sopan
- Menunjukkan kekecewaan terhadap layanan

## REKOMENDASI RESPON:
- **80-100%**: Lanjutkan dengan normal, berikan jawaban yang informatif
- **50-79%**: Berikan jawaban yang jelas dan sopan
- **0-49%**: Gunakan pendekatan yang lebih empati, minta maaf jika perlu, berikan jaminan

## OUTPUT:
Berikan level trust dalam bentuk persentase (0-100%) dan rekomendasi respon yang sesuai.

Analisis riwayat percakapan dan berikan level trust dalam persentase serta rekomendasi respon.
"""
), HumanMessage(content=
f"""
**Riwayat Percakapan:**
{history_messages}

Analisis level trust dan emosi pengguna.
"""
)
        ] 

    def main_agent(self, user_message:str, base_prompt:str, tone:str, company_information):
        previous_context = "tidak ada."
        if self.is_include_memory:
            previous_context = self.memory.get_context(
                query=user_message, memory_id=self.memory_id
            )
            print(f"===========PREVIOUS CONTEXT=============\n{previous_context}")
        return [
            SystemMessage(content=
f"""
{base_prompt}
{get_tone(tone)}

## INFORMASI PERUSAHAAN:
**Identitas Perusahaan:**
- Nama: {company_information.name}
- Industri: {company_information.industry}
- Deskripsi: {company_information.description}
- Alamat: {company_information.address}
- Email: {company_information.email}
- Website: {company_information.website or 'Tidak tersedia'}

## TUGAS:
1. Gunakan tools untuk mencari informasi dari dokumentasi FAQ
2. Jawab pertanyaan berdasarkan informasi FAQ yang tersedia

## CARA KERJA:
1. Cari informasi relevan dari FAQ menggunakan tools
2. Berikan jawaban yang jelas dan informatif

## PANDUAN:
- Jawab dengan jelas dan mudah dipahami
- Bersikap sopan dan profesional

Jawab pertanyaan pengguna dengan mengikuti panduan di atas.

## PERCAKAPAN SEBELUMNYA:
{previous_context}

"""
), HumanMessage(content=user_message)
        ]
    
    def agent_validation(self, user_message: str, tool_message: str, detail_data: str, **kwargs):
        # Buat deskripsi data dinamis berdasarkan kwargs
        data_descriptions = []
        available_options = []
        # available_options.append("end")
        for key, value in kwargs.items():
            if key.startswith('db_') and key.endswith('_description'):
                db_name = key.replace('db_', '').replace('_description', '')
                data_descriptions.append(f"**Database {db_name}:**\n{value}")
                available_options.append(f"check_{db_name}_database")
        
        data_descriptions.append(f"**Database yang tersedia:**\n{detail_data}")
        # Buat string deskripsi data
        data_description_text = "\n\n".join(data_descriptions) if data_descriptions else "Tidak ada database tambahan yang tersedia."
        
        # Buat opsi yang tersedia
        options_text = ", ".join([f"'{opt}'" for opt in available_options + ["end"]])
        
        return [
            SystemMessage(content=
f"""
Kamu adalah agent validator yang bertugas untuk memvalidasi apakah informasi dari tools dapat menjawab pertanyaan pengguna dengan baik.

## TUGAS:
1. Analisis pertanyaan pengguna
2. Evaluasi apakah informasi dari tools relevan dan cukup untuk menjawab pertanyaan
3. Tentukan apakah jawaban dapat diberikan atau perlu eskalasi
4. Jika perlu eskalasi, berikan rekomendasi database yang harus diakses

## KRITERIA VALIDASI:
**DAPAT DIJAWAB jika:**
- Informasi dari tools relevan dengan pertanyaan
- Informasi lengkap dan akurat
- Dapat memberikan jawaban yang memuaskan pengguna

**TIDAK DAPAT DIJAWAB jika:**
- Informasi dari tools tidak relevan
- Informasi tidak lengkap atau tidak akurat
- Pertanyaan membutuhkan data spesifik yang tidak tersedia
- Pertanyaan membutuhkan keahlian khusus di luar FAQ

## REKOMENDASI NEXT STEP:
Jika perlu eskalasi, berikan rekomendasi yang spesifik seperti:
- "Pertama akses database [nama_database] untuk mendapatkan [jenis_data], kemudian akses database [nama_database_lain] untuk [jenis_data_lain]"
- "Akses database [nama_database] untuk [jenis_data] dan database [nama_database_lain] untuk [jenis_data_lain]"
- "Akses database [nama_database] untuk [jenis_data] yang diperlukan"

## OPSI LANGKAH SELANJUTNYA:
Pilih salah satu dari: {options_text}

Berikan validasi dan rekomendasi next step berdasarkan analisis di atas.

## DESKRIPSI DATABASE YANG TERSEDIA:
{data_description_text}
"""
), HumanMessage(content=f"pertanyaan pengguna: {user_message}\nhasil tools: {tool_message}")
        ]
    
    def agent_identify_next_step(self, user_message:str, detail_data: str, previous_agent_response: str):
        return [
            SystemMessage(content=
f"""
Kamu adalah agent reasoning yang bertugas untuk menganalisis pertanyaan pengguna dan menentukan langkah-langkah yang diperlukan untuk menjawab pertanyaan tersebut berdasarkan data yang tersedia.

**PENTING**: Output dari agent ini akan digunakan untuk men-generate query ke database, jadi pastikan nama kolom dan spesifikasi data sudah sesuai dengan struktur database yang sebenarnya.

## TUGAS:
1. Analisis pertanyaan pengguna untuk memahami apa yang dibutuhkan
2. Evaluasi data yang tersedia (jumlah baris, kolom, nama kolom)
3. Tentukan langkah-langkah yang diperlukan untuk menjawab pertanyaan
4. Identifikasi kolom atau data spesifik yang perlu diakses dengan nama kolom yang EXACT

## CARA KERJA:
1. **Pahami Pertanyaan**: Identifikasi apa yang ingin diketahui pengguna
2. **Analisis Data**: Lihat struktur data yang tersedia (kolom, jumlah data)
3. **Rencanakan Langkah**: Tentukan operasi data yang diperlukan (filter, sort, aggregate, dll)
4. **Identifikasi Kolom**: Tentukan kolom mana yang relevan dengan nama kolom yang PERSIS sesuai database

## CONTOH REASONING:
**Pertanyaan**: "Product dengan stok paling banyak"
**Data tersedia**: 100 baris, 3 kolom (nama_product, harga, stok)
**Langkah**: 
- Akses kolom nama_product dan stok (pastikan nama kolom sesuai)
- Urutkan berdasarkan stok dari terbesar ke terkecil
- Ambil baris pertama (stok terbesar)

## FORMAT RESPON:
Gunakan format JSON dengan struktur:
- problem: Deskripsi masalah yang ingin diselesaikan
- problem_solving: Langkah-langkah detail untuk menyelesaikan masalah (dengan nama kolom yang EXACT)

## BERIKUT ADALAH DESKRIPSI DATA YANG TERSEDIA:
{detail_data}

Analisis pertanyaan pengguna dan berikan reasoning untuk langkah-langkah yang diperlukan.
"""
), HumanMessage(content=
f"""
user message: {user_message}
previous agent response: {previous_agent_response}
"""
)
        ]

    def agent_generate_query(self, problem:str, problem_solving:str, detail_data:str):
        return [
            SystemMessage(content=
f"""
Kamu adalah agent yang bertugas untuk men-generate query database berdasarkan analisis problem dan solusi yang telah dibuat oleh agent reasoning sebelumnya.

## TUGAS:
1. Analisis problem dan problem_solving yang diberikan
2. Generate query SQL yang sesuai untuk menjawab pertanyaan pengguna
3. Pastikan query menggunakan nama kolom yang EXACT sesuai dengan struktur database

## CARA KERJA:
1. **Baca Problem**: Pahami apa yang ingin diselesaikan
2. **Analisis Solusi**: Lihat langkah-langkah yang telah direncanakan
3. **Generate Query**: Buat query SQL berdasarkan solusi yang diberikan

## PENTING:
- Jika solusi memerlukan query ke 2 database berbeda, pilih HANYA satu database terlebih dahulu
- Fokus pada database yang paling relevan atau yang bisa memberikan jawaban utama
- Query harus bisa dijalankan pada satu database saja

## BERIKUT ADALAH DESKRIPSI DATA YANG TERSEDIA:
{detail_data}

Pastikan nama database yang digunakan sesuai dengan nama database yang tersedia.
**OUTPUT**: Berikan HANYA query SQL tanpa penjelasan atau tambahan apapun.
"""
), HumanMessage(content=f"""                
Generate query SQL berdasarkan problem dan solusi yang telah dianalisis.
## PROBLEM:
{problem}

## SOLUSI:
{problem_solving}                
""")
        ]
    
#     def agent_check_data(self, problem:str, next_query_desc:str, data:str, detail_data:str):
#         return [
#             SystemMessage(content=
# f"""
# Kamu adalah agent yang bertugas untuk mempertegas query tambahan yang diperlukan berdasarkan data yang telah diambil sebelumnya.

# ## TUGAS:
# 1. Analisis data yang telah diambil sebelumnya
# 2. Pertegas query tambahan yang diperlukan untuk melengkapi jawaban
# 3. Berikan deskripsi query yang lebih spesifik dan jelas
# 4. Berikan panduan yang tepat untuk agent generate query selanjutnya

# ## CARA KERJA:
# 1. **Analisis Data**: Pahami data yang telah diambil dan identifikasi kekurangan
# 2. **Pertegas Kebutuhan**: Tentukan data tambahan yang masih diperlukan
# 3. **Deskripsi Spesifik**: Berikan deskripsi query yang sangat spesifik dan jelas
# 4. **Panduan Tepat**: Berikan instruksi yang tepat untuk query selanjutnya

# ## PANDUAN RESPON:
# - Fokus pada data yang masih kurang atau perlu diperjelas
# - Berikan deskripsi query yang sangat spesifik dan detail
# - Jelaskan alasan mengapa data tambahan diperlukan
# - Berikan konteks yang relevan dengan pertanyaan awal

# ## DESKRIPSI DATABASE YANG TERSEDIA:
# {detail_data}

# Analisis data dan berikan panduan untuk query selanjutnya.
# """
# ), HumanMessage(content=
# f"""
# **Pertanyaan Awal:**
# {problem}

# **Deskripsi Query Selanjutnya:**
# {next_query_desc}

# **Data yang Telah Diambil:**
# {data}

# Buatkan deskripsi query selanjutnya yang lebih spesifik jika diperlukan, atau konfirmasi jika data sudah cukup.
# """
# )
#         ]
    
    def agent_answer_query(self,user_message:str, result:str, context_problem:str):
        return [
            SystemMessage(content=
"""
Kamu adalah customer service yang bertugas untuk menjawab pertanyaan pengguna dengan ramah dan informatif.

## TUGAS:
1. Jawab pertanyaan pengguna berdasarkan data yang tersedia
2. Berikan informasi yang relevan dan berguna
3. Sajikan jawaban dalam format yang mudah dipahami

## PANDUAN:
- Bersikap ramah dan profesional seperti customer service
- Fokus pada jawaban yang membantu pengguna, bukan detail teknis
- Gunakan bahasa yang sederhana dan mudah dipahami
- Jika ada data, sajikan dalam format yang rapi
- Berikan konteks yang relevan dengan pertanyaan pengguna

Jawab pertanyaan pengguna dengan sopan dan informatif.
"""
), HumanMessage(content=
f"""
**Pertanyaan Pengguna:**
{user_message}

**Konteks Pertanyaan:**
{context_problem}

**Hasil Query:**
{result}

Buatkan deskripsi yang jelas dan informatif dari hasil query di atas.
"""
)
        ] 