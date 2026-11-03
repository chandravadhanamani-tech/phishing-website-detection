"""
user.py - User ORM Model
=========================
Defines the 'users' table using SQLAlchemy ORM.
Stores registered user accounts with role-based access control.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    ORM model for the 'users' table.
    
    Roles:
        'user'  - Regular user who can analyze URLs
        'admin' - Administrator with access to system-wide stats
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum("user", "admin"), nullable=False, default="user")
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────────────────────────────
    analyses = relationship("URLAnalysis", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
