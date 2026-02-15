"""
Yahoo Finance provider adapter (yfinance wrapper).
"""

import yfinance as yf
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
from app.services.data_providers.base import (
    DataProvider,
    NewsItem,
    FinancialData,
    TechnicalData,
    HistoricalDataPoint,
    DataSourceEnum,
)
from app.services.news_filter import NewsFilter


class YFinanceProvider(DataProvider):
    """Yahoo Finance data provider via yfinance library."""
    
    def __init__(self):
        super().__init__(api_key=None)  # yfinance doesn't require API key
        self.name = "YFinance"
    
    async def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company info from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Company info dict or None if not found
        """
        try:
            ticker = yf.Ticker(symbol)
            info = {}
            
            # Primary method: standard info
            try:
                info = ticker.info
            except Exception as e:
                print(f"Standard info fetch failed for {symbol}: {e}")

            # Fallback method: fast_info (more reliable for basic data)
            if not info or len(info) < 5:  # Arbitrary threshold for "valid" info
                try:
                    fast = ticker.fast_info
                    # Construct basic info from fast_info
                    if fast and hasattr(fast, 'last_price'):
                        info = {
                            "symbol": symbol,
                            "currency": fast.currency,
                            "currentPrice": fast.last_price,
                            "previousClose": fast.previous_close,
                            "dayHigh": fast.day_high,
                            "dayLow": fast.day_low,
                            "fiftyTwoWeekHigh": fast.year_high,
                            "fiftyTwoWeekLow": fast.year_low,
                            "marketCap": fast.market_cap,
                            "volume": fast.last_volume,
                            # Add defaults for missing fields to avoid frontend crash
                            "longName": symbol,
                            "sector": "Unknown",
                            "industry": "Unknown",
                            "longBusinessSummary": "Data retrieved via fast_info fallback.",
                        }
                except Exception as e:
                    print(f"Fast info fallback failed for {symbol}: {e}")

            if not info:
                return None
            
            # Map to standardized format
            return {
                "symbol": info.get("symbol", symbol),
                "longName": info.get("longName", symbol),
                "currency": info.get("currency", "INR"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "marketCap": info.get("marketCap"),
                "volume": info.get("volume"),
                "averageVolume": info.get("averageVolume"),
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "trailingEps": info.get("trailingEps"),
                "dividendYield": info.get("dividendYield"),
                "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
                "beta": info.get("beta"),
                "longBusinessSummary": info.get("longBusinessSummary", ""),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "currentPrice": info.get("currentPrice"), # Ensure we pass these through if they exist
                "previousClose": info.get("previousClose")
            }
        except Exception as e:
            print(f"YFinance get_info error for {symbol}: {e}")
            return None
    
    async def get_history(
        self, 
        symbol: str, 
        period: str = "1y"
    ) -> Optional[List[HistoricalDataPoint]]:
        """
        Fetch historical price data from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 3y)
            
        Returns:
            List of historical data points or None
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period).reset_index()
            
            if hist.empty:
                return None
            
            data = []
            for _, row in hist.iterrows():
                data_point = HistoricalDataPoint(
                    date=pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                    adjusted_close=float(row.get("Adj Close", row["Close"])),
                )
                data.append(data_point)
            
            return data
        except Exception as e:
            print(f"YFinance get_history error for {symbol}: {e}")
            return None
    
    async def get_news(
        self, 
        symbol: str, 
        limit: int = 10
    ) -> Optional[List[NewsItem]]:
        """
        Fetch recent news articles from Yahoo Finance with sentiment analysis.
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of articles to fetch
            
        Returns:
            List of enriched news items with sentiment and relevance scores
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return None
            
            # Extract company info for better entity matching
            company_name = ""
            try:
                info = ticker.info
                company_name = info.get("longName", "") or info.get("shortName", "")
            except Exception:
                pass
            
            news_items = []
            for item in news[:limit]:
                try:
                    content = item.get("content", item)
                    title = content.get("title") or item.get("title") or item.get("headline")
                    publisher = content.get("provider", {}).get("displayName") or item.get("publisher") or item.get("source")
                    link = content.get("clickThroughUrl", {}).get("url") or content.get("canonicalUrl", {}).get("url") or item.get("link") or item.get("url")
                    published_at = item.get("providerPublishTime") or item.get("publishedAt")
                    
                    if not title:
                        continue
                    
                    # Analyze news with sentiment and entity extraction
                    news_filter = NewsFilter(symbol=symbol, company_name=company_name)
                    analysis = news_filter.analyze_news(
                        title=title,
                        publisher=publisher,
                        link=link,
                        providerPublishTime=published_at,
                    )
                    
                    news_item = NewsItem(
                        title=analysis.title,
                        publisher=analysis.publisher,
                        link=analysis.link,
                        published_at=analysis.providerPublishTime,
                        sentiment=round(analysis.sentiment, 3),
                        relevance_score=round(analysis.relevance_score, 3),
                        matched_entities=analysis.matched_entities,
                        source_provider=DataSourceEnum.YFINANCE.value,
                    )
                    news_items.append(news_item)
                except Exception:
                    continue
            
            return news_items if news_items else None
        except Exception as e:
            print(f"YFinance get_news error for {symbol}: {e}")
            return None
    
    async def get_financials(self, symbol: str) -> Optional[FinancialData]:
        """
        Fetch financial metrics from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Financial data or None
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            return FinancialData(
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                forward_pe=info.get("forwardPE"),
                earnings_per_share=info.get("trailingEps"),
                dividend_yield=info.get("dividendYield"),
                price_to_sales=info.get("priceToSalesTrailing12Months"),
                debt_to_equity=info.get("debtToEquity"),
                current_ratio=info.get("currentRatio"),
                roe=info.get("returnOnEquity"),
                roa=info.get("returnOnAssets"),
                profit_margin=info.get("profitMargin"),
                revenue=info.get("totalRevenue"),
                net_income=info.get("netIncomeToCommon"),
            )
        except Exception as e:
            print(f"YFinance get_financials error for {symbol}: {e}")
            return None
    
    async def is_available(self) -> bool:
        """YFinance is always available (free, no auth needed)."""
        return True
    
    async def rate_limit_status(self) -> Dict[str, Any]:
        """YFinance has no official rate limits (soft cap ~100/min)."""
        return {
            "remaining": None,
            "reset_at": None,
            "limit_per_minute": 100,
            "note": "Soft limit; heavy use may trigger throttling",
        }
