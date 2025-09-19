import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    agent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    file_name = sa.Column(sa.String(100), nullable=False)
    content_type = sa.Column(sa.Enum("pdf", "docs", "txt", "csv", "xlsx", "xls"), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    # relationship
    agent = relationship("Agent", back_populates="documents")

    def __repr__(self):
        return f"<document name={self.file_name} user_id={self.agent_id}>"
