from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from app.db.base_class import Base

class ZerodhaToken(Base):
    __tablename__ = "zerodha_tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    action = Column(Enum("buy", "sell", name="trade_action"))
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        } 