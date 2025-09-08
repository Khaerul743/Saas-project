import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Metadata(Base):
    __tablename__ = "metadata"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    history_message_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("history_messages.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_tokens = sa.Column(sa.Integer, nullable=False)
    response_time = sa.Column(sa.Float, nullable=False)
    model = sa.Column(sa.Enum("gpt-3.5-turbo", "gpt-4o"))
    is_success = sa.Column(sa.Boolean, nullable=False, server_default=sa.text("1"))

    history_message = relationship("HistoryMessage", back_populates="message_metadata")

    def __repr__(self):
        return f"<history_message_id: {self.history_message_id}>"
