import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.config.database import Base


class CompanyInformation(Base):
    __tablename__ = "company_information"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    agent_id = sa.Column(
        sa.String(5),
        sa.ForeignKey("agents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    name = sa.Column(sa.String(100), nullable=False)
    industry = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(1000), nullable=False)
    address = sa.Column(sa.String(100), nullable=False)
    email = sa.Column(sa.String(100), nullable=False)
    website = sa.Column(sa.String(100), nullable=True)
    fallback_email = sa.Column(sa.String(100), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())

    agent = relationship("Agent", back_populates="company_information")
