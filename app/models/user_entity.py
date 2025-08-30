import sqlalchemy as sa

from app.configs.database import Base


class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True, index=True, autoincrement=True)
    name = sa.Column(
        sa.String(100),
        nullable=False,
    )
    email = sa.Column(sa.String(50), unique=True, index=True, nullable=False)
    password = sa.Column(sa.String(100), nullable=False)
    plan = sa.Column(
        sa.Enum("free", "normal", "pro"), nullable=False, server_default="free"
    )
    company_name = sa.Column(sa.String(50), nullable=False)
    role = sa.Column(
        sa.Enum("AI engineer", "sales", "other"), nullable=False, server_default="other"
    )
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
    last_login = sa.Column(sa.DateTime(timezone=True))
    status = sa.Column(
        sa.Enum("active", "non-active"), nullable=False, server_default="active"
    )

    def __repr__(self):
        return f"<User email={self.email} role={self.role}>"
