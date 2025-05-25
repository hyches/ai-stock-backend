from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.db.base_class import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    level = Column(String)  # info, warning, error, critical
    source = Column(String)  # system, trade, websocket, etc.
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        } 