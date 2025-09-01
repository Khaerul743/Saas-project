import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = sa.Column(sa.Integer, primary_key=True, index=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    name = sa.Column(
        sa.String(100),
        nullable=False,
    )
    avatar = sa.Column(sa.String(100), nullable=True)
    model = sa.Column(
        sa.Enum(
            "gpt-3.5-turbo",
            "gpt-4o",
        ),
        nullable=False,
    )
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
        sa.String(1000), nullable=False, server_default="Tidak ada deskripsi"
    )
    status = sa.Column(
        sa.Enum("active", "non-active"), nullable=False, server_default="active"
    )
    base_prompt = sa.Column(
        sa.String(1000), nullable=False, server_default="Tidak ada base prompt tambahan"
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
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    # Relationship
    user = relationship("User", back_populates="agents")

    def __repr__(self):
        return f"<Agent name={self.name} user_id={self.user_id}>"
