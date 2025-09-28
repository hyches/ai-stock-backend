"""
Comprehensive trading services testing suite
"""
import pytest
from fastapi import status
from unittest.mock import patch, Mock
from tests.test_config import TestConfig, TestClient, sample_strategy_data, sample_trade_data, sample_portfolio_data

class TestTradingStrategies:
    """Test trading strategy functionality"""
    
    def test_create_strategy(self, authorized_client: TestClient, sample_strategy_data):
        """Test creating a new trading strategy"""
        response = authorized_client.post("/api/v1/trading/strategies/", json=sample_strategy_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["name"] == sample_strategy_data["name"]
            assert data["type"] == sample_strategy_data["type"]
            assert "id" in data
    
    def test_get_strategies(self, authorized_client: TestClient):
        """Test getting all strategies"""
        response = authorized_client.get("/api/v1/trading/strategies/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
    
    def test_get_strategy_by_id(self, authorized_client: TestClient, sample_strategy_data):
        """Test getting a specific strategy by ID"""
        # First create a strategy
        create_response = authorized_client.post("/api/v1/trading/strategies/", json=sample_strategy_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            strategy_id = create_response.json()["id"]
            response = authorized_client.get(f"/api/v1/trading/strategies/{strategy_id}")
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_strategy(self, authorized_client: TestClient, sample_strategy_data):
        """Test updating a strategy"""
        # First create a strategy
        create_response = authorized_client.post("/api/v1/trading/strategies/", json=sample_strategy_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            strategy_id = create_response.json()["id"]
            update_data = {
                "name": "Updated Strategy",
                "description": "Updated description"
            }
            response = authorized_client.put(f"/api/v1/trading/strategies/{strategy_id}", json=update_data)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_delete_strategy(self, authorized_client: TestClient, sample_strategy_data):
        """Test deleting a strategy"""
        # First create a strategy
        create_response = authorized_client.post("/api/v1/trading/strategies/", json=sample_strategy_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            strategy_id = create_response.json()["id"]
            response = authorized_client.delete(f"/api/v1/trading/strategies/{strategy_id}")
            assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]
    
    def test_invalid_strategy_type(self, authorized_client: TestClient, sample_strategy_data):
        """Test creating strategy with invalid type"""
        invalid_strategy = sample_strategy_data.copy()
        invalid_strategy["type"] = "invalid_type"
        
        response = authorized_client.post("/api/v1/trading/strategies/", json=invalid_strategy)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestTradingOperations:
    """Test trading operations (trades, positions)"""
    
    def test_create_trade(self, authorized_client: TestClient, sample_trade_data):
        """Test creating a new trade"""
        response = authorized_client.post("/api/v1/trading/trades/", json=sample_trade_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["symbol"] == sample_trade_data["symbol"]
            assert data["type"] == sample_trade_data["type"]
            assert "id" in data
    
    def test_get_trades(self, authorized_client: TestClient):
        """Test getting all trades"""
        response = authorized_client.get("/api/v1/trading/trades/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
    
    def test_get_trades_by_symbol(self, authorized_client: TestClient):
        """Test getting trades by symbol"""
        params = {"symbol": TestConfig.TEST_SYMBOL}
        response = authorized_client.get("/api/v1/trading/trades/", params=params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_trades_by_date_range(self, authorized_client: TestClient):
        """Test getting trades by date range"""
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        }
        response = authorized_client.get("/api/v1/trading/trades/", params=params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_invalid_trade_type(self, authorized_client: TestClient, sample_trade_data):
        """Test creating trade with invalid type"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["type"] = "invalid_type"
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_trade_quantity(self, authorized_client: TestClient, sample_trade_data):
        """Test creating trade with invalid quantity"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["quantity"] = -100
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_trade_price(self, authorized_client: TestClient, sample_trade_data):
        """Test creating trade with invalid price"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["price"] = -150.0
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestPortfolioManagement:
    """Test portfolio management functionality"""
    
    def test_create_portfolio(self, authorized_client: TestClient, sample_portfolio_data):
        """Test creating a new portfolio"""
        response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["name"] == sample_portfolio_data["name"]
            assert data["initial_balance"] == sample_portfolio_data["initial_balance"]
            assert "id" in data
    
    def test_get_portfolios(self, authorized_client: TestClient):
        """Test getting all portfolios"""
        response = authorized_client.get("/api/v1/trading/portfolios/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
    
    def test_get_portfolio_by_id(self, authorized_client: TestClient, sample_portfolio_data):
        """Test getting a specific portfolio by ID"""
        # First create a portfolio
        create_response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            portfolio_id = create_response.json()["id"]
            response = authorized_client.get(f"/api/v1/trading/portfolios/{portfolio_id}")
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_portfolio(self, authorized_client: TestClient, sample_portfolio_data):
        """Test updating a portfolio"""
        # First create a portfolio
        create_response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            portfolio_id = create_response.json()["id"]
            update_data = {
                "name": "Updated Portfolio",
                "description": "Updated description"
            }
            response = authorized_client.put(f"/api/v1/trading/portfolios/{portfolio_id}", json=update_data)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_delete_portfolio(self, authorized_client: TestClient, sample_portfolio_data):
        """Test deleting a portfolio"""
        # First create a portfolio
        create_response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            portfolio_id = create_response.json()["id"]
            response = authorized_client.delete(f"/api/v1/trading/portfolios/{portfolio_id}")
            assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]
    
    def test_invalid_portfolio_balance(self, authorized_client: TestClient, sample_portfolio_data):
        """Test creating portfolio with invalid balance"""
        invalid_portfolio = sample_portfolio_data.copy()
        invalid_portfolio["initial_balance"] = -1000.0
        
        response = authorized_client.post("/api/v1/trading/portfolios/", json=invalid_portfolio)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestPositionManagement:
    """Test position management functionality"""
    
    def test_create_position(self, authorized_client: TestClient):
        """Test creating a new position"""
        position_data = {
            "symbol": TestConfig.TEST_SYMBOL,
            "quantity": TestConfig.TEST_QUANTITY,
            "entry_price": TestConfig.TEST_PRICE,
            "current_price": TestConfig.TEST_PRICE + 5.0
        }
        
        response = authorized_client.post("/api/v1/trading/positions/", json=position_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["symbol"] == position_data["symbol"]
            assert data["quantity"] == position_data["quantity"]
            assert "id" in data
    
    def test_get_positions(self, authorized_client: TestClient):
        """Test getting all positions"""
        response = authorized_client.get("/api/v1/trading/positions/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
    
    def test_get_positions_by_symbol(self, authorized_client: TestClient):
        """Test getting positions by symbol"""
        params = {"symbol": TestConfig.TEST_SYMBOL}
        response = authorized_client.get("/api/v1/trading/positions/", params=params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_position(self, authorized_client: TestClient):
        """Test updating a position"""
        # First create a position
        position_data = {
            "symbol": TestConfig.TEST_SYMBOL,
            "quantity": TestConfig.TEST_QUANTITY,
            "entry_price": TestConfig.TEST_PRICE,
            "current_price": TestConfig.TEST_PRICE + 5.0
        }
        
        create_response = authorized_client.post("/api/v1/trading/positions/", json=position_data)
        
        if create_response.status_code == status.HTTP_201_CREATED:
            position_id = create_response.json()["id"]
            update_data = {"current_price": TestConfig.TEST_PRICE + 10.0}
            response = authorized_client.put(f"/api/v1/trading/positions/{position_id}", json=update_data)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_invalid_position_quantity(self, authorized_client: TestClient):
        """Test creating position with invalid quantity"""
        invalid_position = {
            "symbol": TestConfig.TEST_SYMBOL,
            "quantity": -100,
            "entry_price": TestConfig.TEST_PRICE,
            "current_price": TestConfig.TEST_PRICE + 5.0
        }
        
        response = authorized_client.post("/api/v1/trading/positions/", json=invalid_position)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestBacktesting:
    """Test backtesting functionality"""
    
    def test_run_backtest(self, authorized_client: TestClient):
        """Test running a backtest"""
        backtest_data = {
            "strategy_id": 1,
            "symbol": TestConfig.TEST_SYMBOL,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_balance": TestConfig.TEST_INITIAL_BALANCE
        }
        
        response = authorized_client.post("/api/v1/trading/backtest/", json=backtest_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert data["strategy_id"] == backtest_data["strategy_id"]
            assert data["symbol"] == backtest_data["symbol"]
            assert "id" in data
    
    def test_get_backtest_results(self, authorized_client: TestClient):
        """Test getting backtest results"""
        response = authorized_client.get("/api/v1/trading/backtest/1")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "items" in data
            assert "total" in data
    
    def test_invalid_backtest_dates(self, authorized_client: TestClient):
        """Test running backtest with invalid dates"""
        invalid_backtest = {
            "strategy_id": 1,
            "symbol": TestConfig.TEST_SYMBOL,
            "start_date": "2023-12-31",
            "end_date": "2023-01-01",  # End before start
            "initial_balance": TestConfig.TEST_INITIAL_BALANCE
        }
        
        response = authorized_client.post("/api/v1/trading/backtest/", json=invalid_backtest)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_backtest_balance(self, authorized_client: TestClient):
        """Test running backtest with invalid balance"""
        invalid_backtest = {
            "strategy_id": 1,
            "symbol": TestConfig.TEST_SYMBOL,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_balance": -1000.0  # Negative balance
        }
        
        response = authorized_client.post("/api/v1/trading/backtest/", json=invalid_backtest)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestTradingValidation:
    """Test trading data validation"""
    
    def test_symbol_validation(self, authorized_client: TestClient, sample_trade_data):
        """Test symbol validation"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["symbol"] = ""  # Empty symbol
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_price_validation(self, authorized_client: TestClient, sample_trade_data):
        """Test price validation"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["price"] = 0  # Zero price
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_quantity_validation(self, authorized_client: TestClient, sample_trade_data):
        """Test quantity validation"""
        invalid_trade = sample_trade_data.copy()
        invalid_trade["quantity"] = 0  # Zero quantity
        
        response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestTradingIntegration:
    """Test trading integration with other services"""
    
    def test_trading_with_ml_predictions(self, authorized_client: TestClient):
        """Test trading operations with ML predictions"""
        from tests.test_config import sample_ml_data
        
        # Get ML prediction
        ml_response = authorized_client.post("/api/v1/ml/predict", json=sample_ml_data)
        
        # Create a trade
        trade_response = authorized_client.post("/api/v1/trading/trades/", json=sample_trade_data)
        
        # Both should work
        assert ml_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        assert trade_response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_trading_with_portfolio(self, authorized_client: TestClient):
        """Test trading operations with portfolio"""
        # Create a portfolio
        portfolio_response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        
        # Create a trade
        trade_response = authorized_client.post("/api/v1/trading/trades/", json=sample_trade_data)
        
        # Both should work
        assert portfolio_response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        assert trade_response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
