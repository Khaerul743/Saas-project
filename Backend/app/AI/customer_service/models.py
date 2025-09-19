from typing import Annotated, List, Literal, Optional, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field, create_model


def create_validation_agent_model(available_databases: List[str]):
    """
    Membuat model validation agent yang dinamis berdasarkan database yang tersedia

    Args:
        available_databases: List nama database yang tersedia, contoh: ["products", "orders", "customers"]

    Returns:
        Class model yang bisa digunakan untuk structured output
    """
    # Buat opsi next_step berdasarkan database yang tersedia
    next_step_options = []
    for db in available_databases:
        next_step_options.append(f"check_{db}_database")
    next_step_options.append("end")

    # Buat Literal type dinamis
    NextStepType = Literal[tuple(next_step_options)]

    # Buat deskripsi yang dinamis
    options_str = ", ".join([f"'{opt}'" for opt in next_step_options])
    description = f"Langkah selanjutnya untuk menjawab pertanyaan. Pilih: {options_str}"

    # Buat model dinamis
    return create_model(
        "StructuredOutputValidationAgent",
        can_answer=(
            bool,
            Field(description="Apakah tools dapat menjawab pertanyaan dengan baik"),
        ),
        reasoning=(
            str,
            Field(
                description="langkah selanjutnya untuk menjawab pertanyaan, contoh: 'Pertama akses A products untuk mendapatkan data A, kemudian akses database B untuk mendapatkan data B'"
            ),
        ),
        next_step=(NextStepType, Field(description=description)),
        __base__=BaseModel,
    )


class StructuredOutputTrustLevelCheck(BaseModel):
    trust_level: int = Field(description="Level trust dalam persentase (0-100%)")
    message: Optional[str] = Field(
        description="Pernyataan kepada pengguna bahwa kamu akan mengirim keluhan pengguna ke tim kami"
    )
    problem: Optional[str] = Field(description="Masalah yang dialami pengguna")


# Default model untuk backward compatibility
class StructuredOutputValidationAgent(BaseModel):
    can_answer: bool = Field(
        description="Apakah tools dapat menjawab pertanyaan dengan baik"
    )
    reasoning: str = Field(
        description="Alasan untuk tidak menjawab pertanyaan dengan tools"
    )
    next_step: Literal["check_product_database", "end"] = Field(
        description="Langkah selanjutnya untuk menjawab pertanyaan"
    )


class StructuredOutputIdentifyNextStep(BaseModel):
    problem: str = Field(description="Apa yang ingin diselesaikan")
    problem_solving: str = Field(description="Bagaimana cara menyelesaikan masalah")


class StructuredOutputGenerateQuery(BaseModel):
    query: str = Field(
        description="Query SQL yang akan digunakan untuk menjawab pertanyaan"
    )
    file_path: str = Field(description="Path file database yang akan digunakan.")
    db_name: str = Field(description="Nama database yang akan digunakan.")
    query_again: bool = Field(description="Apakah harus query ke database lagi?")
    next_query_desc: Optional[str] = Field(
        description="Deskripsikan query yang akan dilakukan selanjutnya"
    )


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_message: str = "none"
    trust_level: int = 100
    message_for_user: str = "none"
    user_problem: str = "none"
    response: str = "none"
    total_token: int = 0
    include_data: bool = False
    can_answer: bool = True
    reason: str = "none"
    next_step: str = "none"
    problem: str = "none"
    problem_solving: str = "none"
    detail_data: str = "none"
    db_name: str = "none"
    query: str = "none"
    result: str = "none"
    data: str = "data:"
    query_again: bool = False
    next_query_desc: Optional[str] = "none"


if __name__ == "__main__":
    available_databases = ["products", "orders", "customers"]
    model = create_validation_agent_model(available_databases)
    print(model.model_json_schema())
