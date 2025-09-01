import sqlalchemy as sa

from app.configs.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = sa.Column(sa.Integer, primary_key=True, index=True, autoincrement=True)
    name = sa.Column(
        sa.String(100),
        nullable=False,
    )
    avatar = sa.Column(sa.String(100), nullable=True)
    role = sa.Column(
        sa.Enum(
            "simple RAG agent",
            "customer service",
            "data analyst",
            "finance assistant",
            "sales",
        ),
        nullable=False,
        server_default="simple RAG agent",
    )
    description = sa.Column(
        sa.String, nullable=False, server_default="Tidak ada deskripsi"
    )
    status = sa.Column(
        sa.Enum("active", "non-active"), nullable=False, server_default="active"
    )
    base_prompt = sa.Column(
        sa.String, nullable=False, server_default="Tidak ada base prompt tambahan"
    )
    short_term_memory = sa.Column(
        sa.BOOLEAN, nullable=False, server_default=sa.text("0")
    )
    long_term_memory = sa.Column(
        sa.BOOLEAN, nullable=False, server_default=sa.text("0")
    )
    tone = sa.Column(
        sa.Enum("formal", "friendly", "casual", "profesional"),
        nullable=False,
        server_default="formal",
    )
