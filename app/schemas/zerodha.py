from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HistoricalDataRequest(BaseModel):
    symbol: str
    from_date: str
    to_date: str
    interval: str = Field(default="day", pattern="^(minute|5minute|15minute|30minute|60minute|day)$")

class HistoricalDataResponse(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class PaperTradeCreate(BaseModel):
    symbol: str
    action: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class PaperTradeResponse(BaseModel):
    id: int
    symbol: str
    action: str
    quantity: int
    price: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True 