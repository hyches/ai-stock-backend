from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - using string references to avoid circular imports
    portfolios = relationship("Portfolio", back_populates="user", lazy="select")
    strategies = relationship("Strategy", back_populates="user", lazy="select")
    reports = relationship("Report", back_populates="user", lazy="select")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission
        """
        return self.is_superuser or permission in self.permissions

    @property
    def has_permissions(self, permissions: set) -> bool:
        """
        Check if user has all specified permissions
        """
        return self.is_superuser or permissions.issubset(set(self.permissions)) 