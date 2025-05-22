import pytest
from app.models.stock import StockIn
from app.services.screener import StockScreener
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

@pytest.fixture
def mock_stock_data():
    """Fixture for mock stock data"""
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "price": 150.0,
        "volume": 1000000,
        "market_cap": 2500000,  # in millions
        "pe_ratio": 25.0,
        "dividend_yield": 0.5,
        "ma_50": 145.0,
        "ma_200": 140.0,
        "last_updated": datetime.utcnow()
    }

@pytest.fixture
def screener():
    """Fixture for StockScreener instance"""
    return StockScreener()

@pytest.mark.asyncio
async def test_screen_stocks_basic(screener, mock_stock_data):
    """Test basic stock screening functionality"""
    # Mock the fetch_stock_data function
    with patch('app.services.screener.fetch_stock_data') as mock_fetch:
        mock_fetch.return_value = mock_stock_data
        
        # Create test criteria
        criteria = StockIn(
            sector="Technology",
            min_volume=500000,
            max_pe=30,
            min_market_cap=1000000,
            min_price=100,
            max_price=200,
            min_dividend_yield=0.0
        )
        
        # Screen stocks
        results = await screener.screen_stocks(criteria)
        
        # Verify results
        assert len(results) > 0
        assert results[0].symbol == "AAPL"
        assert results[0].sector == "Technology"
        assert results[0].price == 150.0

@pytest.mark.asyncio
async def test_screen_stocks_no_matches(screener, mock_stock_data):
    """Test screening with criteria that should match no stocks"""
    with patch('app.services.screener.fetch_stock_data') as mock_fetch:
        mock_fetch.return_value = mock_stock_data
        
        # Create strict criteria
        criteria = StockIn(
            sector="Healthcare",  # Different sector
            min_volume=2000000,   # Higher volume
            max_pe=10,            # Lower P/E
            min_market_cap=5000000,  # Higher market cap
            min_price=200,        # Higher price
            max_price=300,
            min_dividend_yield=2.0  # Higher dividend yield
        )
        
        # Screen stocks
        results = await screener.screen_stocks(criteria)
        
        # Verify no matches
        assert len(results) == 0

@pytest.mark.asyncio
async def test_screen_stocks_technical_analysis(screener, mock_stock_data):
    """Test screening with technical analysis criteria"""
    with patch('app.services.screener.fetch_stock_data') as mock_fetch:
        mock_fetch.return_value = mock_stock_data
        
        # Create criteria with technical analysis
        criteria = StockIn(
            sector="Technology",
            min_volume=500000,
            max_pe=30,
            min_market_cap=1000000,
            min_price=100,
            max_price=200,
            min_dividend_yield=0.0
        )
        
        # Screen stocks
        results = await screener.screen_stocks(criteria)
        
        # Verify technical analysis
        assert len(results) > 0
        assert results[0].ma_50 > results[0].ma_200  # Golden cross condition

@pytest.mark.asyncio
async def test_screen_stocks_error_handling(screener):
    """Test error handling in stock screening"""
    with patch('app.services.screener.fetch_stock_data') as mock_fetch:
        mock_fetch.return_value = None  # Simulate failed data fetch
        
        criteria = StockIn(
            sector="Technology",
            min_volume=500000
        )
        
        # Screen stocks
        results = await screener.screen_stocks(criteria)
        
        # Verify empty results on error
        assert len(results) == 0

@pytest.mark.asyncio
async def test_screen_stocks_batch_processing(screener, mock_stock_data):
    """Test batch processing of stocks"""
    with patch('app.services.screener.fetch_stock_data') as mock_fetch:
        # Create multiple mock responses
        mock_fetch.side_effect = [
            mock_stock_data,
            {**mock_stock_data, "symbol": "MSFT"},
            {**mock_stock_data, "symbol": "GOOGL"}
        ]
        
        criteria = StockIn(
            sector="Technology",
            min_volume=500000
        )
        
        # Screen stocks
        results = await screener.screen_stocks(criteria)
        
        # Verify batch processing
        assert len(results) == 3
        assert {r.symbol for r in results} == {"AAPL", "MSFT", "GOOGL"} 