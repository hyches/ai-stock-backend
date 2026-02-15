"""
Abstract base classes for data providers.

Defines the interface that all stock data providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DataSourceEnum(str, Enum):
    """Supported data sources"""
    YFINANCE = "yfinance"
    ALPHAVANTAGE = "alphavantage"
    FINNHUB = "finnhub"
    FMP = "fmp"
    CACHED = "cached"


@dataclass
class NewsItem:
    """Standardized news article representation"""
    title: str
    publisher: Optional[str] = None
    link: Optional[str] = None
    published_at: Optional[int] = None  # Unix timestamp
    summary: Optional[str] = None
    sentiment: Optional[float] = None  # -1 to +1
    relevance_score: Optional[float] = None  # 0 to 1
    source_provider: Optional[str] = None
    matched_entities: Optional[Dict[str, List[str]]] = None  # company, sector, keywords


@dataclass
class FinancialData:
    """Standardized financial metrics"""
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    earnings_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    price_to_sales: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    profit_margin: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None


@dataclass
class TechnicalData:
    """Technical indicators"""
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi_14: Optional[float] = None
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    obv: Optional[float] = None  # On-Balance Volume


@dataclass
class HistoricalDataPoint:
    """Single OHLCV data point"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None


@dataclass
class StockData:
    """Complete standardized stock data"""
    symbol: str
    company_name: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    business_summary: Optional[str] = None
    
    # Market data
    current_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[float] = None
    avg_volume: Optional[float] = None
    beta: Optional[float] = None
    
    # Historical data
    history: List[HistoricalDataPoint] = None
    
    # News
    news: List[NewsItem] = None
    
    # Financials
    financials: Optional[FinancialData] = None
    
    # Technicals
    technicals: Optional[TechnicalData] = None
    
    # Metadata
    source: Optional[str] = None  # Which provider returned this
    cached: bool = False
    fetched_at: Optional[datetime] = None


class DataProvider(ABC):
    """
    Abstract base class for stock data providers.
    
    All providers must implement these methods.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize provider with optional API key.
        
        Args:
            api_key: API key for the provider (if required)
        """
        self.api_key = api_key
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company info and basic metrics.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with company info or None if not found
        """
        pass
    
    @abstractmethod
    async def get_history(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[HistoricalDataPoint]]:
        """
        Fetch historical price data.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 3y)
            
        Returns:
            List of historical data points or None
        """
        pass
    
    @abstractmethod
    async def get_news(self, symbol: str, limit: int = 10) -> Optional[List[NewsItem]]:
        """
        Fetch recent news articles.
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of articles to fetch
            
        Returns:
            List of news items or None
        """
        pass
    
    async def get_financials(self, symbol: str) -> Optional[FinancialData]:
        """
        Fetch financial metrics. Optional (default: not implemented).
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Financial data or None
        """
        return None
    
    async def get_technicals(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[TechnicalData]:
        """
        Fetch or compute technical indicators. Optional (default: not implemented).
        
        Args:
            symbol: Stock ticker symbol
            period: Time period
            
        Returns:
            Technical data or None
        """
        return None
    
    async def get_options(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch options chains. Optional (default: not implemented).
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Options data or None
        """
        return None
    
    async def is_available(self) -> bool:
        """
        Check if provider is available (API key valid, no errors).
        
        Returns:
            True if provider is ready, False otherwise
        """
        return True
    
    async def rate_limit_status(self) -> Dict[str, Any]:
        """
        Get rate limit status for the provider.
        
        Returns:
            Dict with remaining calls, reset time, etc.
        """
        return {"remaining": None, "reset_at": None}
