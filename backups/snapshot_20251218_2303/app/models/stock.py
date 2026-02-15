from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class StockIn(BaseModel):
    """Input model for stock screening criteria"""
    sector: Optional[str] = Field(None, description="Stock sector (e.g., 'Technology', 'Finance')")
    min_volume: Optional[float] = Field(None, description="Minimum trading volume")
    max_pe: Optional[float] = Field(None, description="Maximum P/E ratio")
    min_market_cap: Optional[float] = Field(None, description="Minimum market capitalization in millions")
    min_price: Optional[float] = Field(None, description="Minimum stock price")
    max_price: Optional[float] = Field(None, description="Maximum stock price")
    min_dividend_yield: Optional[float] = Field(None, description="Minimum dividend yield percentage")

    @validator('min_volume', 'min_market_cap', 'min_price', 'max_price', 'min_dividend_yield')
    def validate_positive_numbers(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v

    @validator('max_pe')
    def validate_pe_ratio(cls, v):
        if v is not None and v <= 0:
            raise ValueError('P/E ratio must be positive')
        return v

class StockOut(BaseModel):
    """Output model for stock screening results"""
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    sector: str = Field(..., description="Stock sector")
    price: float = Field(..., description="Current stock price")
    volume: float = Field(..., description="Trading volume")
    market_cap: float = Field(..., description="Market capitalization in millions")
    pe_ratio: Optional[float] = Field(None, description="Price to Earnings ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    ma_50: Optional[float] = Field(None, description="50-day moving average")
    ma_200: Optional[float] = Field(None, description="200-day moving average")
    last_updated: datetime = Field(..., description="Last data update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "price": 175.50,
                "volume": 50000000,
                "market_cap": 2800000.0,
                "pe_ratio": 28.5,
                "dividend_yield": 0.5,
                "ma_50": 172.30,
                "ma_200": 165.80,
                "last_updated": "2024-02-20T15:30:00Z"
            }
        } 