import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.config.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    agent_id = sa.Column(
        sa.String(5),
        sa.ForeignKey("agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    api_key = sa.Column(sa.String(100), nullable=False)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    user = relationship("User", back_populates="api_keys")
    agent = relationship("Agent", back_populates="api_keys")

    def __repr__(self):
        return f"<user_id={self.user_id} api_key={self.api_key}>"
