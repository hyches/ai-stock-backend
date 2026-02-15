"""
Data Provider abstraction layer for multi-source stock data.

Provides pluggable interfaces to fetch stock data from multiple sources
(Yahoo Finance, Alpha Vantage, Finnhub, Financial Modeling Prep) with
intelligent fallback and caching.
"""

from .base import DataProvider, StockData, NewsItem, FinancialData
from .provider_router import ProviderRouter

__all__ = [
    "DataProvider",
    "StockData",
    "NewsItem",
    "FinancialData",
    "ProviderRouter",
]
