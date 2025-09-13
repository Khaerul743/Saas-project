import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.configs.database import Base


class Platform(Base):
    __tablename__ = "platforms"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    integration_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("integrations.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    platform_type = sa.Column(sa.Enum("telegram", "api"), nullable=False)
    api_key = sa.Column(sa.String(100), nullable=False)

    integration = relationship("Integration", back_populates="platform_config")

    def __repr__(self):
        return f"<integration_id={self.integration_id} platform_type={self.platform_type} api_key={self.api_key}>"
