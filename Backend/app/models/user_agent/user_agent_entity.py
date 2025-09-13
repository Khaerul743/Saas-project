import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class UserAgent(Base):
    __tablename__ = "user_agents"
    id = sa.Column(sa.String(50), nullable=False, primary_key=True)
    agent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    username = sa.Column(sa.String(50), nullable=False)
    user_platform = sa.Column(sa.Enum("telegram", "whatsapp", "api"), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    # Relations
    agent = relationship("Agent", back_populates="user_agents")
    history_messages = relationship(
        "HistoryMessage",
        back_populates="user_agents",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
