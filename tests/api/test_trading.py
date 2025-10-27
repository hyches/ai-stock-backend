import pytest
from fastapi import status
from app.models.trading import Strategy, Trade, Position, BacktestResult
from app.models.portfolio import PortfolioOutput as Portfolio

def test_create_strategy(authorized_client, test_strategy):
    """Test creating a new strategy"""
    response = authorized_client.post("/api/v1/strategies/", json=test_strategy)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == test_strategy["name"]
    assert data["type"] == test_strategy["type"]
    assert "id" in data

from app.models.trading import Strategy as StrategyModel

def test_get_strategies(authorized_client, test_strategy, db):
    """Test getting all strategies"""
    # Create a strategy first
    strategy = StrategyModel(**test_strategy)
    db.add(strategy)
    db.commit()
    
    response = authorized_client.get("/api/v1/strategies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_strategy(authorized_client, test_strategy, db):
    """Test getting a specific strategy"""
    # Create a strategy first
    strategy = StrategyModel(**test_strategy)
    db.add(strategy)
    db.commit()
    
    response = authorized_client.get(f"/api/v1/strategies/{strategy.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == strategy.id
    assert data["name"] == test_strategy["name"]

def test_update_strategy(authorized_client, test_strategy, db):
    """Test updating a strategy"""
    # Create a strategy first
    strategy = StrategyModel(**test_strategy)
    db.add(strategy)
    db.commit()
    
    update_data = {
        "name": "Updated Strategy",
        "description": "Updated description"
    }
    
    response = authorized_client.put(
        f"/api/v1/strategies/{strategy.id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_strategy(authorized_client, test_strategy, db):
    """Test deleting a strategy"""
    # Create a strategy first
    strategy = StrategyModel(**test_strategy)
    db.add(strategy)
    db.commit()
    
    response = authorized_client.delete(f"/api/v1/strategies/{strategy.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify strategy is deleted
    get_response = authorized_client.get(f"/api/v1/strategies/{strategy.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_create_trade(authorized_client, test_trade):
    """Test creating a new trade"""
    response = authorized_client.post("/api/v1/trades/", json=test_trade)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == test_trade["symbol"]
    assert data["type"] == test_trade["type"]
    assert "id" in data

def test_get_trades(authorized_client, test_trade):
    """Test getting all trades"""
    # Create a trade first
    authorized_client.post("/api/v1/trades/", json=test_trade)
    
    response = authorized_client.get("/api/v1/trades/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_create_portfolio(authorized_client, test_portfolio):
    """Test creating a new portfolio"""
    response = authorized_client.post("/api/v1/portfolios/", json=test_portfolio)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == test_portfolio["name"]
    assert data["initial_balance"] == test_portfolio["initial_balance"]
    assert "id" in data

def test_get_portfolios(authorized_client, test_portfolio):
    """Test getting all portfolios"""
    # Create a portfolio first
    authorized_client.post("/api/v1/portfolios/", json=test_portfolio)
    
    response = authorized_client.get("/api/v1/portfolios/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_create_position(authorized_client, test_position):
    """Test creating a new position"""
    response = authorized_client.post("/api/v1/positions/", json=test_position)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == test_position["symbol"]
    assert data["quantity"] == test_position["quantity"]
    assert "id" in data

def test_get_positions(authorized_client, test_position):
    """Test getting all positions"""
    # Create a position first
    authorized_client.post("/api/v1/positions/", json=test_position)
    
    response = authorized_client.get("/api/v1/positions/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_run_backtest(authorized_client, test_backtest):
    """Test running a backtest"""
    response = authorized_client.post("/api/v1/backtests/", json=test_backtest)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["strategy_id"] == test_backtest["strategy_id"]
    assert data["symbol"] == test_backtest["symbol"]
    assert "id" in data

def test_get_backtest_results(authorized_client, test_backtest):
    """Test getting backtest results"""
    # Run a backtest first
    authorized_client.post("/api/v1/backtests/", json=test_backtest)
    
    response = authorized_client.get(f"/api/v1/backtests/{test_backtest['strategy_id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

from fastapi.testclient import TestClient
from app.main import app

def test_unauthorized_access():
    """Test unauthorized access to endpoints"""
    client = TestClient(app)
    endpoints = [
        "/api/v1/strategies/",
        "/api/v1/trades/",
        "/api/v1/portfolios/",
        "/api/v1/positions/",
        "/api/v1/backtests/"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_strategy_type(authorized_client, test_strategy):
    """Test creating strategy with invalid type"""
    invalid_strategy = test_strategy.copy()
    invalid_strategy["type"] = "invalid_type"
    
    response = authorized_client.post("/api/v1/strategies/", json=invalid_strategy)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_trade_type(authorized_client, test_trade):
    """Test creating trade with invalid type"""
    invalid_trade = test_trade.copy()
    invalid_trade["type"] = "invalid_type"
    
    response = authorized_client.post("/api/v1/trades/", json=invalid_trade)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_portfolio_balance(authorized_client, test_portfolio):
    """Test creating portfolio with invalid balance"""
    invalid_portfolio = test_portfolio.copy()
    invalid_portfolio["initial_balance"] = -1000.0
    
    response = authorized_client.post("/api/v1/portfolios/", json=invalid_portfolio)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_position_quantity(authorized_client, test_position):
    """Test creating position with invalid quantity"""
    invalid_position = test_position.copy()
    invalid_position["quantity"] = -100
    
    response = authorized_client.post("/api/v1/positions/", json=invalid_position)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_backtest_dates(authorized_client, test_backtest):
    """Test running backtest with invalid dates"""
    invalid_backtest = test_backtest.copy()
    invalid_backtest["start_date"] = "2023-12-31"
    invalid_backtest["end_date"] = "2023-01-01"
    
    response = authorized_client.post("/api/v1/backtests/", json=invalid_backtest)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 