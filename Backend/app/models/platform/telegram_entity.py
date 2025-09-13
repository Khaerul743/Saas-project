import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Telegram(Base):
    __tablename__ = "telegram"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    integration_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("integrations.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,  # Supaya jadi one-to-one
        nullable=False,
    )
    api_key = sa.Column(sa.String(100), nullable=False)

    # Telegram -> Integration
    integration = relationship("Integration", back_populates="telegram")

    def __repr__(self):
        return f"<integrations_id> : {self.integration_id}"
