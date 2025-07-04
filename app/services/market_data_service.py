from typing import Dict, List, Optional
import logging
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from app.core.cache import redis_cache

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour
        self.symbol_mapping = {
            "NIFTY 50": "^NSEI",
            "BANK NIFTY": "^NSEBANK",
            "RELIANCE": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "INFY": "INFY.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "HDFC": "HDFC.NS",
            "SBIN": "SBIN.NS"
        }

    async def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "1d"
    ) -> List[Dict]:
        """Get historical data from Yahoo Finance"""
        try:
            # Convert interval to yfinance format
            yf_interval = self._convert_interval(interval)
            
            # Get data from cache first
            cache_key = f"historical:{symbol}:{from_date.date()}:{to_date.date()}:{interval}"
            cached_data = await redis_cache.get(cache_key)
            if cached_data:
                return cached_data

            # Get data from Yahoo Finance
            ticker = yf.Ticker(self.symbol_mapping.get(symbol, f"{symbol}.NS"))
            df = ticker.history(
                start=from_date,
                end=to_date,
                interval=yf_interval
            )

            # Convert to list of dicts
            data = []
            for index, row in df.iterrows():
                data.append({
                    "date": index.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })

            # Cache the data
            await redis_cache.set(cache_key, data, self.cache_ttl)
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            raise

    async def get_live_quote(self, symbol: str) -> Dict:
        """Get live quote from Yahoo Finance"""
        try:
            # Get from cache first
            cache_key = f"quote:{symbol}"
            cached_quote = await redis_cache.get(cache_key)
            if cached_quote:
                return cached_quote

            # Get live quote
            ticker = yf.Ticker(self.symbol_mapping.get(symbol, f"{symbol}.NS"))
            info = ticker.info

            quote = {
                "symbol": symbol,
                "last_price": info.get("regularMarketPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0),
                "volume": info.get("regularMarketVolume", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "open": info.get("regularMarketOpen", 0),
                "previous_close": info.get("regularMarketPreviousClose", 0),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Cache for 1 minute
            await redis_cache.set(cache_key, quote, 60)
            return quote
        except Exception as e:
            logger.error(f"Error fetching live quote for {symbol}: {str(e)}")
            raise

    def _convert_interval(self, interval: str) -> str:
        """Convert our interval format to yfinance format"""
        mapping = {
            "minute": "1m",
            "5minute": "5m",
            "15minute": "15m",
            "30minute": "30m",
            "60minute": "1h",
            "day": "1d"
        }
        return mapping.get(interval, "1d")

    async def get_market_status(self) -> Dict:
        """Get current market status"""
        try:
            # Get NSE status
            nifty = yf.Ticker("^NSEI")
            info = nifty.info

            return {
                "is_market_open": info.get("marketState", "") == "REGULAR",
                "last_updated": datetime.utcnow().isoformat(),
                "market_cap": info.get("marketCap", 0),
                "volume": info.get("regularMarketVolume", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching market status: {str(e)}")
            raise 