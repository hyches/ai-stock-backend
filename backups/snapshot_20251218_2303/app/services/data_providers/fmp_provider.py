"""
Financial Modeling Prep (FMP) provider adapter.

FMP specializes in financial statements and fundamentals.
"""

from typing import Optional, Dict, Any, List
from app.services.data_providers.base import (
    DataProvider,
    FinancialData,
    HistoricalDataPoint,
)


class FMPProvider(DataProvider):
    """Financial Modeling Prep provider - best for fundamentals."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key=api_key)
        self.name = "FMP"
        
        if api_key and api_key != "demo_key_replace_with_your_actual_key":
            self.base_url = "https://financialmodelingprep.com/api/v3"
            self.available = True
        else:
            self.available = False
    
    async def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company info from FMP.
        
        FMP provides detailed company profile data.
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            # Stub: FMP profile endpoint
            # Full implementation would call /profile/{symbol}
            return None
        except Exception as e:
            print(f"FMP get_info error for {symbol}: {e}")
            return None
    
    async def get_history(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[HistoricalDataPoint]]:
        """
        Fetch historical price data from FMP.
        
        Note: FMP's strength is financials, not historical data.
        Use yfinance for this.
        """
        # Stub: FMP has historical data but yfinance is faster
        # Return None to fallback to yfinance
        return None
    
    async def get_financials(self, symbol: str) -> Optional[FinancialData]:
        """
        Fetch comprehensive financial metrics from FMP.
        
        FMP excels at financial statements and metrics.
        """
        if not self.available or not self.api_key:
            return None
        
        try:
            # Stub: FMP financial statements endpoints
            # /income-statement/{symbol}
            # /balance-sheet-statement/{symbol}
            # /cash-flow-statement/{symbol}
            # /financial-ratios/{symbol}
            return None
        except Exception as e:
            print(f"FMP get_financials error for {symbol}: {e}")
            return None
    
    async def is_available(self) -> bool:
        """Check if FMP is available."""
        return self.available
    
    async def rate_limit_status(self) -> Dict[str, Any]:
        """Get FMP rate limit status."""
        return {
            "limit_per_day": 250,
            "current_usage": "Unknown",
            "note": "Free tier: 250 calls/day; sufficient for research",
        }
