import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Integration(Base):
    __tablename__ = "integrations"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    agent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    platform = sa.Column(sa.Enum("whatsapp", "telegram", "api"), nullable=False)
    status = sa.Column(
        sa.Enum("active", "non-active"), nullable=False, server_default="active"
    )
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    # Integration -> Agent
    agent = relationship("Agent", back_populates="integrations")

    # Integration -> Telegram (One-to-One)
    telegram = relationship(
        "Telegram",
        back_populates="integration",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # Integration -> Api (One-to-One)
    api = relationship(
        "Api",
        back_populates="integration",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<agent_id={self.agent_id} platform={self.platform}>"
