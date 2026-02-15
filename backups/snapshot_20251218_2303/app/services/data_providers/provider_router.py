"""
Intelligent provider router for multi-source data fetching.

Routes requests to the best available provider with fallback logic.
"""

from typing import Optional, List, Dict, Any
from app.core.config import Settings
from app.services.data_providers.base import (
    DataProvider,
    NewsItem,
    FinancialData,
    TechnicalData,
    HistoricalDataPoint,
    StockData,
)
from app.services.data_providers.yfinance_provider import YFinanceProvider
from app.services.data_providers.alphavantage_provider import AlphaVantageProvider
from app.services.data_providers.finnhub_provider import FinnhubProvider
from app.services.data_providers.fmp_provider import FMPProvider
import logging
from app.services.request_coalescer import RequestCoalescer
from app.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class ProviderRouter:
    """
    Routes data requests to the best provider with intelligent fallback.
    
    Prioritizes:
    - Cache (fastest)
    - Configured providers (API keys present)
    - Rate limits (uses providers with available quota)
    - Fallback chain (tries alternatives on failure)
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize router with all available providers.
        
        Args:
            settings: Application settings with API keys
        """
        self.settings = settings
        self.logger = logger
        
        # Initialize providers
        self.yfinance = YFinanceProvider()
        self.alphavantage = AlphaVantageProvider(settings.ALPHA_VANTAGE_API_KEY)
        self.finnhub = FinnhubProvider(settings.FINNHUB_API_KEY)
        self.fmp = FMPProvider(settings.FMP_API_KEY)
        # Request coalescer to prevent duplicate concurrent upstream calls
        self.coalescer = RequestCoalescer()
        # Rate limiter config: provider -> (capacity, refill_interval_seconds)
        rl_config = {
            "alphavantage": (settings.ALPHAVANTAGE_RATE_LIMIT, 60),
            "finnhub": (settings.FINNHUB_RATE_LIMIT, 60),
            # FMP uses daily limit; approximate by minute window for dev
            "fmp": (max(1, settings.FMP_RATE_LIMIT // 1440), 60),
        }
        self.rate_limiter = RateLimiter(rl_config)
        
        # Provider chains by data type (priority order)
        self.provider_chains = {
            "news": [self.finnhub, self.alphavantage, self.yfinance],
            "financials": [self.fmp, self.alphavantage, self.yfinance],
            "history": [self.yfinance, self.alphavantage],
            "info": [self.yfinance, self.finnhub, self.alphavantage],
            "technicals": [self.yfinance],  # Compute from history
            "options": [self.yfinance],  # Only source available
        }
    
    async def get_news(
        self,
        symbol: str,
        limit: int = 10,
        force_provider: Optional[str] = None,
    ) -> Optional[List[NewsItem]]:
        """
        Fetch news with intelligent provider fallback.
        
        Tries in order: Finnhub → AlphaVantage → YFinance
        
        Args:
            symbol: Stock ticker
            limit: Number of articles
            force_provider: Force specific provider (debug/test)
            
        Returns:
            List of news items or None
        """
        # Use request coalescing per-symbol+limit to avoid duplicate fetches
        key = f"news:{symbol}:{limit}:{force_provider or 'auto'}"
        return await self.coalescer.coalesce(key, self._fetch_news, symbol, limit, force_provider)

    async def _fetch_news(self, symbol: str, limit: int = 10, force_provider: Optional[str] = None) -> Optional[List[NewsItem]]:
        """Internal: actual news fetch with fallback chain."""
        if force_provider:
            provider = self._get_provider_by_name(force_provider)
            if provider:
                return await provider.get_news(symbol, limit)

        for provider in self.provider_chains["news"]:
            try:
                # Respect rate limiter and circuit breaker per provider
                allowed = await self.rate_limiter.allow(provider.name)
                if not allowed:
                    self.logger.warning(f"Rate limited or circuit open for {provider.name}; skipping for {symbol}")
                    continue

                self.logger.info(f"Fetching news for {symbol} via {provider.name}")
                news = await provider.get_news(symbol, limit)
                if news:
                    self.rate_limiter.record_success(provider.name)
                    self.logger.info(f"News fetched from {provider.name}: {len(news)} items")
                    return news
                else:
                    # Treat empty result as a failure to allow breaker to count
                    self.rate_limiter.record_failure(provider.name)
            except Exception as e:
                self.rate_limiter.record_failure(provider.name)
                self.logger.warning(f"{provider.name} news fetch failed for {symbol}: {e}")
                continue

        self.logger.warning(f"All providers failed to fetch news for {symbol}")
        return None
    
    async def get_history(
        self,
        symbol: str,
        period: str = "1y",
        force_provider: Optional[str] = None,
    ) -> Optional[List[HistoricalDataPoint]]:
        """
        Fetch historical data with fallback.
        
        Tries in order: YFinance → AlphaVantage
        
        Args:
            symbol: Stock ticker
            period: Time period (1mo, 3mo, 6mo, 1y, 3y)
            force_provider: Force specific provider
            
        Returns:
            List of historical data points or None
        """
        key = f"history:{symbol}:{period}:{force_provider or 'auto'}"
        return await self.coalescer.coalesce(key, self._fetch_history, symbol, period, force_provider)

    async def _fetch_history(self, symbol: str, period: str = "1y", force_provider: Optional[str] = None) -> Optional[List[HistoricalDataPoint]]:
        """Internal: actual history fetch with fallback chain."""
        if force_provider:
            provider = self._get_provider_by_name(force_provider)
            if provider:
                return await provider.get_history(symbol, period)

        for provider in self.provider_chains["history"]:
            try:
                allowed = await self.rate_limiter.allow(provider.name)
                if not allowed:
                    self.logger.warning(f"Rate limited or circuit open for {provider.name}; skipping history for {symbol}")
                    continue

                self.logger.info(f"Fetching history for {symbol} ({period}) via {provider.name}")
                history = await provider.get_history(symbol, period)
                if history:
                    self.rate_limiter.record_success(provider.name)
                    self.logger.info(f"History fetched from {provider.name}: {len(history)} points")
                    return history
                else:
                    self.rate_limiter.record_failure(provider.name)
            except Exception as e:
                self.rate_limiter.record_failure(provider.name)
                self.logger.warning(f"{provider.name} history fetch failed for {symbol}: {e}")
                continue

        self.logger.warning(f"All providers failed to fetch history for {symbol}")
        return None
    
    async def get_info(
        self,
        symbol: str,
        force_provider: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch company info with fallback.
        
        Tries in order: YFinance → Finnhub → AlphaVantage
        
        Args:
            symbol: Stock ticker
            force_provider: Force specific provider
            
        Returns:
            Company info dict or None
        """
        key = f"info:{symbol}:{force_provider or 'auto'}"
        return await self.coalescer.coalesce(key, self._fetch_info, symbol, force_provider)

    async def _fetch_info(self, symbol: str, force_provider: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Internal: actual info fetch with fallback chain."""
        if force_provider:
            provider = self._get_provider_by_name(force_provider)
            if provider:
                return await provider.get_info(symbol)

        for provider in self.provider_chains["info"]:
            try:
                allowed = await self.rate_limiter.allow(provider.name)
                if not allowed:
                    self.logger.warning(f"Rate limited or circuit open for {provider.name}; skipping info for {symbol}")
                    continue

                self.logger.info(f"Fetching info for {symbol} via {provider.name}")
                info = await provider.get_info(symbol)
                if info:
                    self.rate_limiter.record_success(provider.name)
                    self.logger.info(f"Info fetched from {provider.name}")
                    return info
                else:
                    self.rate_limiter.record_failure(provider.name)
            except Exception as e:
                self.rate_limiter.record_failure(provider.name)
                self.logger.warning(f"{provider.name} info fetch failed for {symbol}: {e}")
                continue

        self.logger.warning(f"All providers failed to fetch info for {symbol}")
        return None
    
    async def get_financials(
        self,
        symbol: str,
        force_provider: Optional[str] = None,
    ) -> Optional[FinancialData]:
        """
        Fetch financial metrics with fallback.
        
        Tries in order: FMP → AlphaVantage → YFinance
        
        Args:
            symbol: Stock ticker
            force_provider: Force specific provider
            
        Returns:
            Financial data or None
        """
        key = f"financials:{symbol}:{force_provider or 'auto'}"
        return await self.coalescer.coalesce(key, self._fetch_financials, symbol, force_provider)

    async def _fetch_financials(self, symbol: str, force_provider: Optional[str] = None) -> Optional[FinancialData]:
        """Internal: actual financials fetch with fallback chain."""
        if force_provider:
            provider = self._get_provider_by_name(force_provider)
            if provider:
                return await provider.get_financials(symbol)

        for provider in self.provider_chains["financials"]:
            try:
                allowed = await self.rate_limiter.allow(provider.name)
                if not allowed:
                    self.logger.warning(f"Rate limited or circuit open for {provider.name}; skipping financials for {symbol}")
                    continue

                self.logger.info(f"Fetching financials for {symbol} via {provider.name}")
                financials = await provider.get_financials(symbol)
                if financials:
                    self.rate_limiter.record_success(provider.name)
                    self.logger.info(f"Financials fetched from {provider.name}")
                    return financials
                else:
                    self.rate_limiter.record_failure(provider.name)
            except Exception as e:
                self.rate_limiter.record_failure(provider.name)
                self.logger.warning(f"{provider.name} financials fetch failed for {symbol}: {e}")
                continue

        self.logger.warning(f"All providers failed to fetch financials for {symbol}")
        return None
    
    def _get_provider_by_name(self, name: str) -> Optional[DataProvider]:
        """Get provider by name."""
        providers = {
            "yfinance": self.yfinance,
            "alphavantage": self.alphavantage,
            "finnhub": self.finnhub,
            "fmp": self.fmp,
        }
        return providers.get(name.lower())
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        return {
            "yfinance": {
                "available": await self.yfinance.is_available(),
                "rate_limit": await self.yfinance.rate_limit_status(),
            },
            "alphavantage": {
                "available": await self.alphavantage.is_available(),
                "rate_limit": await self.alphavantage.rate_limit_status(),
            },
            "finnhub": {
                "available": await self.finnhub.is_available(),
                "rate_limit": await self.finnhub.rate_limit_status(),
            },
            "fmp": {
                "available": await self.fmp.is_available(),
                "rate_limit": await self.fmp.rate_limit_status(),
            },
        }
