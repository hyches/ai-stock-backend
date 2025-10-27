import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.optimizer import PortfolioOptimizer
from app.services.market_data_service import MarketDataService
from app.models.portfolio import PortfolioOutput
import pandas as pd
import numpy as np
from datetime import datetime

@pytest.fixture
def mock_market_data_service():
    """Provides a mock of the MarketDataService."""
    service = MagicMock(spec=MarketDataService)
    service.get_historical_data = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_optimizer_initialization(mock_market_data_service):
    """
    Tests that the PortfolioOptimizer initializes correctly with its dependencies.
    """
    with patch('app.services.optimizer.RandomForestRegressor') as mock_rf:
        optimizer = PortfolioOptimizer(mock_market_data_service)
        assert optimizer.market_data_service == mock_market_data_service
        mock_rf.assert_called_once_with(n_estimators=100, random_state=42)

@pytest.mark.asyncio
async def test_optimize_portfolio_successful_run(mock_market_data_service):
    """
    Tests a successful run of the optimize method with mocked external calls.
    """
    # Mock historical data returned by the market data service
    mock_data = {
        'date': [datetime(2023, 1, 1), datetime(2023, 1, 2)],
        'symbol': ['AAPL', 'AAPL'],
        'close': [150, 152]
    }
    mock_market_data_service.get_historical_data.return_value = mock_data

    with patch('app.services.optimizer.RandomForestRegressor') as mock_rf:
        # Mock the prediction from the RandomForest model
        mock_rf.return_value.predict.return_value = np.array([0.05, 0.03])

        optimizer = PortfolioOptimizer(mock_market_data_service)

        stocks = ["AAPL", "GOOGL"]
        capital = 100000

        result = await optimizer.optimize(stocks, capital)

        assert isinstance(result, PortfolioOutput)
        assert len(result.weights) == len(stocks)
        assert result.cash_allocation is not None
        mock_market_data_service.get_historical_data.assert_awaited_once()

@pytest.mark.asyncio
async def test_optimize_handles_no_historical_data(mock_market_data_service):
    """
    Tests that the optimizer raises a ValueError when no historical data is returned.
    """
    # Simulate the market data service returning no data
    mock_market_data_service.get_historical_data.return_value = []

    optimizer = PortfolioOptimizer(mock_market_data_service)

    with pytest.raises(ValueError, match="Failed to fetch historical data"):
        await optimizer.optimize(["AAPL"], 100000)

def test_data_preparation_logic():
    """
    Tests the internal _prepare_data method to ensure it correctly calculates features.
    This is a synchronous test as it doesn't involve async operations.
    """
    # Patch the ML model loading during optimizer initialization
    with patch('app.services.optimizer.RandomForestRegressor'):
        # The constructor expects a positional argument for the market_data_service
        optimizer = PortfolioOptimizer(MagicMock(spec=MarketDataService))

    # Create a sample DataFrame with enough data for a 20-day window
    data = {
        'AAPL': list(range(100, 124)),
        'GOOGL': list(range(200, 224))
    }
    df = pd.DataFrame(data)

    features, returns = optimizer._prepare_data(df)

    assert 'AAPL_momentum' in features.columns
    assert 'GOOGL_volatility' in features.columns
    assert not features.isnull().values.any()
    assert len(returns) == 2
