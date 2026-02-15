"""
Finnhub provider adapter.

Finnhub is excellent for news, fundamentals, and earnings data.
"""

from typing import Optional, Dict, Any, List
from app.services.data_providers.base import (
    DataProvider,
    NewsItem,
    FinancialData,
    HistoricalDataPoint,
)


class FinnhubProvider(DataProvider):
    """Finnhub data provider - best for news and fundamentals."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.name = "Finnhub"
        
        if api_key and api_key != "demo_key_replace_with_your_actual_key":
            try:
                import finnhub
                self.client = finnhub.Client(api_key=api_key)
                self.available = True
            except Exception as e:
                print(f"Finnhub initialization error: {e}")
                self.available = False
        else:
            self.available = False
    
    async def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company info from Finnhub.
        
        Finnhub provides company profiles with sector, industry, etc.
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            # Stub: Finnhub company profile
            # Full implementation would call client.company_profile()
            return None
        except Exception as e:
            print(f"Finnhub get_info error for {symbol}: {e}")
            return None
    
    async def get_history(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[HistoricalDataPoint]]:
        """
        Fetch historical price data from Finnhub.
        
        Note: Finnhub is better for news/fundamentals than historical data.
        Use yfinance for this.
        """
        # Stub: Finnhub has limited historical data support
        # Return None to fallback to yfinance
        return None
    
    async def get_news(
        self, 
        symbol: str, 
        limit: int = 10
    ) -> Optional[List[NewsItem]]:
        """
        Fetch company news from Finnhub.
        
        Finnhub provides high-quality news with company matching.
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            # Stub: Finnhub company news endpoint
            # Full implementation would call client.company_news()
            # and map to NewsItem dataclass
            return None
        except Exception as e:
            print(f"Finnhub get_news error for {symbol}: {e}")
            return None
    
    async def get_financials(self, symbol: str) -> Optional[FinancialData]:
        """
        Fetch financial metrics from Finnhub.
        
        Finnhub provides earnings estimates, recommendation, and fundamentals.
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            # Stub: Finnhub financials endpoints
            # client.basic_financials()
            return None
        except Exception as e:
            print(f"Finnhub get_financials error for {symbol}: {e}")
            return None
    
    async def is_available(self) -> bool:
        """Check if Finnhub is available."""
        return self.available
    
    async def rate_limit_status(self) -> Dict[str, Any]:
        """Get Finnhub rate limit status."""
        return {
            "limit_per_minute": 60,
            "limit_per_month": 60000,
            "current_usage": "Unknown",
            "note": "Free tier: 60 calls/min, good for most use cases",
        }
