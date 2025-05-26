from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.db.base_class import Base

class Alert(Base):
    """
    Alert class is an ORM model, representing system alerts with various attributes and methods to handle conversion of an alert object to dictionary format.
    Parameters:
        - id (Integer): Unique identifier for each alert.
        - message (String): Descriptive message explaining the alert.
        - level (String): The severity level of the alert, such as info, warning, error, or critical.
        - source (String): Origin of the alert, e.g., system, trade, websocket, etc.
        - metadata (JSON): Additional data related to the alert in JSON format.
        - created_at (DateTime): Timestamp marking when the alert was created, defaults to current UTC time.
        - resolved_at (DateTime): Timestamp marking when the alert was resolved, can be null if unresolved.
    Processing Logic:
        - Supports converting object to dictionary for serialization purposes.
        - Automatically formats timestamps to ISO 8601 strings for standardized representation.
        - Ensures `resolved_at` outputs `None` when unset or undefined, preserving data integrity.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    level = Column(String)  # info, warning, error, critical
    source = Column(String)  # system, trade, websocket, etc.
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert the object's attributes to a dictionary format.
        Parameters:
            - self (object): The instance of the class containing attributes to be converted.
        Returns:
            - dict: A dictionary representation of the object's attributes, adhering to specific key-value pairs.
        Processing Logic:
            - Converts `created_at` and `resolved_at` timestamps to ISO 8601 format.
            - Sets `resolved_at` to `None` if it is not available or undefined."""
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        } 