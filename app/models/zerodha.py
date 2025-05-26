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
    """
    Represents a paper trade entity used for storing simulated trade data.
    Parameters:
        - id (Integer): Unique identifier for the paper trade.
        - symbol (String): The stock symbol associated with the trade.
        - action (Enum): Specifies if the trade action is either a 'buy' or 'sell'.
        - quantity (Integer): The number of shares involved in the trade.
        - price (Float): The price per share at the time of the trade.
        - status (String): The current status of the trade.
        - created_at (DateTime): Timestamp indicating when the trade entry was created, defaulting to the current UTC time.
    Processing Logic:
        - Converts 'created_at' attribute to ISO format when transforming attributes to a dictionary representation.
    """
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    action = Column(Enum("buy", "sell", name="trade_action"))
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert object attributes to a dictionary format.
        Parameters:
            None
        Returns:
            - dict: A dictionary representation of the object's attributes.
        Processing Logic:
            - Converts the 'created_at' attribute to ISO format before adding to the dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        } 