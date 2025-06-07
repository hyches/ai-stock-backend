import pytest
from fastapi import status
from app.models.trading import Strategy, Trade, Portfolio, Position, BacktestResult

def test_create_strategy(authorized_client, test_strategy):
    """Test creating a new strategy"""
    response = authorized_client.post("/api/v1/trading/strategies/", json=test_strategy)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == test_strategy["name"]
    assert data["type"] == test_strategy["type"]
    assert "id" in data

def test_get_strategies(authorized_client, test_strategy):
    """Test getting all strategies"""
    # Create a strategy first
    authorized_client.post("/api/v1/trading/strategies/", json=test_strategy)
    
    response = authorized_client.get("/api/v1/trading/strategies/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_get_strategy(authorized_client, test_strategy):
    """Test getting a specific strategy"""
    # Create a strategy first
    create_response = authorized_client.post("/api/v1/trading/strategies/", json=test_strategy)
    strategy_id = create_response.json()["id"]
    
    response = authorized_client.get(f"/api/v1/trading/strategies/{strategy_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == strategy_id
    assert data["name"] == test_strategy["name"]

def test_update_strategy(authorized_client, test_strategy):
    """Test updating a strategy"""
    # Create a strategy first
    create_response = authorized_client.post("/api/v1/trading/strategies/", json=test_strategy)
    strategy_id = create_response.json()["id"]
    
    update_data = {
        "name": "Updated Strategy",
        "description": "Updated description"
    }
    
    response = authorized_client.put(
        f"/api/v1/trading/strategies/{strategy_id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_strategy(authorized_client, test_strategy):
    """Test deleting a strategy"""
    # Create a strategy first
    create_response = authorized_client.post("/api/v1/trading/strategies/", json=test_strategy)
    strategy_id = create_response.json()["id"]
    
    response = authorized_client.delete(f"/api/v1/trading/strategies/{strategy_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify strategy is deleted
    get_response = authorized_client.get(f"/api/v1/trading/strategies/{strategy_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_create_trade(authorized_client, test_trade):
    """Test creating a new trade"""
    response = authorized_client.post("/api/v1/trading/trades/", json=test_trade)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == test_trade["symbol"]
    assert data["type"] == test_trade["type"]
    assert "id" in data

def test_get_trades(authorized_client, test_trade):
    """Test getting all trades"""
    # Create a trade first
    authorized_client.post("/api/v1/trading/trades/", json=test_trade)
    
    response = authorized_client.get("/api/v1/trading/trades/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_create_portfolio(authorized_client, test_portfolio):
    """Test creating a new portfolio"""
    response = authorized_client.post("/api/v1/trading/portfolios/", json=test_portfolio)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == test_portfolio["name"]
    assert data["initial_balance"] == test_portfolio["initial_balance"]
    assert "id" in data

def test_get_portfolios(authorized_client, test_portfolio):
    """Test getting all portfolios"""
    # Create a portfolio first
    authorized_client.post("/api/v1/trading/portfolios/", json=test_portfolio)
    
    response = authorized_client.get("/api/v1/trading/portfolios/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_create_position(authorized_client, test_position):
    """Test creating a new position"""
    response = authorized_client.post("/api/v1/trading/positions/", json=test_position)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == test_position["symbol"]
    assert data["quantity"] == test_position["quantity"]
    assert "id" in data

def test_get_positions(authorized_client, test_position):
    """Test getting all positions"""
    # Create a position first
    authorized_client.post("/api/v1/trading/positions/", json=test_position)
    
    response = authorized_client.get("/api/v1/trading/positions/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_run_backtest(authorized_client, test_backtest):
    """Test running a backtest"""
    response = authorized_client.post("/api/v1/trading/backtest/", json=test_backtest)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["strategy_id"] == test_backtest["strategy_id"]
    assert data["symbol"] == test_backtest["symbol"]
    assert "id" in data

def test_get_backtest_results(authorized_client, test_backtest):
    """Test getting backtest results"""
    # Run a backtest first
    authorized_client.post("/api/v1/trading/backtest/", json=test_backtest)
    
    response = authorized_client.get(f"/api/v1/trading/backtest/{test_backtest['strategy_id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0

def test_unauthorized_access(client):
    """Test unauthorized access to endpoints"""
    endpoints = [
        "/api/v1/trading/strategies/",
        "/api/v1/trading/trades/",
        "/api/v1/trading/portfolios/",
        "/api/v1/trading/positions/",
        "/api/v1/trading/backtest/"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_strategy_type(authorized_client, test_strategy):
    """Test creating strategy with invalid type"""
    invalid_strategy = test_strategy.copy()
    invalid_strategy["type"] = "invalid_type"
    
    response = authorized_client.post("/api/v1/trading/strategies/", json=invalid_strategy)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_trade_type(authorized_client, test_trade):
    """Test creating trade with invalid type"""
    invalid_trade = test_trade.copy()
    invalid_trade["type"] = "invalid_type"
    
    response = authorized_client.post("/api/v1/trading/trades/", json=invalid_trade)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_portfolio_balance(authorized_client, test_portfolio):
    """Test creating portfolio with invalid balance"""
    invalid_portfolio = test_portfolio.copy()
    invalid_portfolio["initial_balance"] = -1000.0
    
    response = authorized_client.post("/api/v1/trading/portfolios/", json=invalid_portfolio)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_position_quantity(authorized_client, test_position):
    """Test creating position with invalid quantity"""
    invalid_position = test_position.copy()
    invalid_position["quantity"] = -100
    
    response = authorized_client.post("/api/v1/trading/positions/", json=invalid_position)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_backtest_dates(authorized_client, test_backtest):
    """Test running backtest with invalid dates"""
    invalid_backtest = test_backtest.copy()
    invalid_backtest["start_date"] = "2023-12-31"
    invalid_backtest["end_date"] = "2023-01-01"
    
    response = authorized_client.post("/api/v1/trading/backtest/", json=invalid_backtest)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 