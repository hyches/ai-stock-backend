from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HistoricalDataRequest(BaseModel):
    instrument_token: int
    from_date: datetime
    to_date: datetime
    interval: str = Field(default="day", regex="^(minute|5minute|15minute|30minute|60minute|day)$")

class HistoricalDataResponse(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class PaperTradeCreate(BaseModel):
    symbol: str
    action: str = Field(..., regex="^(buy|sell)$")
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class PaperTradeResponse(BaseModel):
    """
    Represents the response of a paper trade transaction.
    Parameters:
        - id (int): Unique identifier for the trade.
        - symbol (str): The trading symbol, e.g., 'AAPL'.
        - action (str): The trade action, e.g., 'buy' or 'sell'.
        - quantity (int): The number of units traded.
        - price (float): The trade price per unit.
        - status (str): Current status of the trade, e.g., 'completed'.
        - created_at (datetime): Timestamp when the trade was executed.
    Processing Logic:
        - Inherits configurations from BaseModel for data validation and processing.
        - Ensures compatibility with attribute-based initialization through Config.
    """
    id: int
    symbol: str
    action: str
    quantity: int
    price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True 