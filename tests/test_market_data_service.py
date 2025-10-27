import pytest
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from app.services.market_data_service import MarketDataService
from app.core.cache import Cache
from datetime import datetime
import pandas as pd

@pytest.fixture
def mock_cache():
    """Provides a MagicMock of the Cache service with async methods."""
    cache_instance = MagicMock(spec=Cache)
    cache_instance.get = AsyncMock()
    cache_instance.set = AsyncMock()
    return cache_instance

@pytest.mark.asyncio
async def test_get_historical_data_fetches_from_api(mock_cache):
    """
    Tests that historical data is fetched from yfinance API when it's not available in the cache.
    """
    mock_cache.get.return_value = None  # Simulate cache miss

    with patch('yfinance.Ticker') as mock_ticker:
        # Prepare mock DataFrame as yfinance would return
        data = {'Open': [100], 'High': [110], 'Low': [90], 'Close': [105], 'Volume': [1000]}
        index = pd.to_datetime(['2023-01-01'])
        mock_df = pd.DataFrame(data, index=index)
        mock_ticker.return_value.history.return_value = mock_df

        service = MarketDataService(mock_cache)
        result = await service.get_historical_data("AAPL", datetime(2023, 1, 1), datetime(2023, 1, 2))

        assert len(result) == 1
        assert result[0]['open'] == 100
        mock_cache.get.assert_awaited_once()
        mock_cache.set.assert_awaited_once()
        mock_ticker.return_value.history.assert_called_once()

@pytest.mark.asyncio
async def test_get_historical_data_from_cache(mock_cache):
    """
    Tests that historical data is returned from the cache when available.
    """
    cached_data = [{'date': '2023-01-01T00:00:00', 'open': 100.0}]
    mock_cache.get.return_value = cached_data

    service = MarketDataService(mock_cache)

    with patch('yfinance.Ticker') as mock_ticker:
        result = await service.get_historical_data("AAPL", datetime(2023, 1, 1), datetime(2023, 1, 2))

        assert result == cached_data
        mock_cache.get.assert_awaited_once()
        mock_ticker.return_value.history.assert_not_called()

@pytest.mark.asyncio
async def test_get_live_quote_fetches_from_api(mock_cache):
    """
    Tests that live quote data is fetched from yfinance API when not in cache.
    """
    mock_cache.get.return_value = None  # Simulate cache miss

    with patch('yfinance.Ticker') as mock_ticker:
        mock_info = {'regularMarketPrice': 150.0, 'regularMarketChange': 1.0}
        # Mock the .info property of the Ticker object
        type(mock_ticker.return_value).info = PropertyMock(return_value=mock_info)

        service = MarketDataService(mock_cache)
        result = await service.get_live_quote("AAPL")

        assert result['last_price'] == 150.0
        assert result['change'] == 1.0
        mock_cache.get.assert_awaited_once()
        mock_cache.set.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_live_quote_from_cache(mock_cache):
    """
    Tests that live quote data is returned from the cache when available.
    """
    cached_quote = {"symbol": "AAPL", "last_price": 150.0, "change": 1.0}
    mock_cache.get.return_value = cached_quote

    service = MarketDataService(mock_cache)

    # Patch yfinance to ensure it is not called
    with patch('yfinance.Ticker') as mock_ticker:
        result = await service.get_live_quote("AAPL")

        assert result == cached_quote
        mock_cache.get.assert_awaited_once()
        mock_ticker.return_value.history.assert_not_called()
