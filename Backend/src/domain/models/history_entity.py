import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.config.database import Base


class HistoryMessage(Base):
    __tablename__ = "history_messages"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_agent_id = sa.Column(
        sa.String(50),
        sa.ForeignKey("user_agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_message = sa.Column(sa.Text, nullable=False)
    response = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    user_agents = relationship("UserAgent", back_populates="history_messages")
    message_metadata = relationship(
        "Metadata",
        back_populates="history_message",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<agent_id: {self.agent_id}, thread_id: {self.thread_id}>"
