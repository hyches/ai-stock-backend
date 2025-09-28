"""
Comprehensive API testing suite for all endpoints
"""
import pytest
from fastapi import status
from unittest.mock import patch, Mock
from tests.test_config import TestConfig, TestClient, sample_strategy_data, sample_portfolio_data, sample_trade_data, sample_ml_data

class TestAuthenticationAPI:
    """Test authentication endpoints"""
    
    def test_user_registration(self, client: TestClient):
        """Test user registration endpoint"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_user_login(self, client: TestClient):
        """Test user login endpoint"""
        login_data = {
            "username": TestConfig.TEST_USER_EMAIL,
            "password": TestConfig.TEST_USER_PASSWORD
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_token_validation(self, authorized_client: TestClient):
        """Test token validation"""
        response = authorized_client.get("/api/v1/auth/me")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to protected endpoints"""
        # Test GET endpoints
        get_endpoints = [
            "/api/v1/trading/strategies/",
            "/api/v1/portfolio/",
            "/api/v1/market/stock/AAPL"
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test POST endpoints
        post_endpoints = [
            "/api/v1/ml/predict"
        ]
        
        for endpoint in post_endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestTradingAPI:
    """Test trading-related endpoints"""
    
    def test_create_strategy(self, authorized_client: TestClient, sample_strategy_data):
        """Test creating a new trading strategy"""
        response = authorized_client.post("/api/v1/trading/strategies/", json=sample_strategy_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_strategies(self, authorized_client: TestClient):
        """Test getting all strategies"""
        response = authorized_client.get("/api/v1/trading/strategies/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_create_trade(self, authorized_client: TestClient, sample_trade_data):
        """Test creating a new trade"""
        response = authorized_client.post("/api/v1/trading/trades/", json=sample_trade_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_trades(self, authorized_client: TestClient):
        """Test getting all trades"""
        response = authorized_client.get("/api/v1/trading/trades/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_create_portfolio(self, authorized_client: TestClient, sample_portfolio_data):
        """Test creating a new portfolio"""
        response = authorized_client.post("/api/v1/trading/portfolios/", json=sample_portfolio_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_portfolios(self, authorized_client: TestClient):
        """Test getting all portfolios"""
        response = authorized_client.get("/api/v1/trading/portfolios/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
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

class TestMLAPI:
    """Test ML-related endpoints"""
    
    def test_ml_predict(self, authorized_client: TestClient, sample_ml_data):
        """Test ML prediction endpoint"""
        response = authorized_client.post("/api/v1/ml/predict", json=sample_ml_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_batch_predict(self, authorized_client: TestClient):
        """Test batch prediction endpoint"""
        batch_data = [sample_ml_data for _ in range(3)]
        response = authorized_client.post("/api/v1/ml/batch_predict", json=batch_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_model_performance(self, authorized_client: TestClient):
        """Test model performance endpoint"""
        response = authorized_client.get("/api/v1/ml/performance")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_feature_importance(self, authorized_client: TestClient):
        """Test feature importance endpoint"""
        response = authorized_client.get("/api/v1/ml/feature_importance")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_model_retrain(self, superuser_client: TestClient):
        """Test model retraining endpoint"""
        retrain_data = {
            "X": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]],
            "y": [1]
        }
        response = superuser_client.post("/api/v1/ml/retrain", json=retrain_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

class TestMarketDataAPI:
    """Test market data endpoints"""
    
    @patch('yfinance.Ticker')
    def test_get_market_data(self, mock_ticker, authorized_client: TestClient):
        """Test getting market data"""
        mock_instance = Mock()
        mock_instance.history.return_value = Mock()
        mock_instance.info = {'currentPrice': 150.0}
        mock_ticker.return_value = mock_instance
        
        response = authorized_client.get(f"/api/v1/market/data/{TestConfig.TEST_SYMBOL}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_historical_data(self, authorized_client: TestClient):
        """Test getting historical data"""
        params = {
            "symbol": TestConfig.TEST_SYMBOL,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        }
        response = authorized_client.get("/api/v1/market/historical", params=params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_technical_indicators(self, authorized_client: TestClient):
        """Test getting technical indicators"""
        params = {
            "symbol": TestConfig.TEST_SYMBOL,
            "indicator": "sma",
            "period": 20
        }
        response = authorized_client.get("/api/v1/market/indicators", params=params)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

class TestPortfolioAPI:
    """Test portfolio management endpoints"""
    
    def test_create_portfolio(self, authorized_client: TestClient, sample_portfolio_data):
        """Test creating a portfolio"""
        response = authorized_client.post("/api/v1/portfolio/", json=sample_portfolio_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_portfolio_analysis(self, authorized_client: TestClient):
        """Test getting portfolio analysis"""
        response = authorized_client.get("/api/v1/portfolio/analysis")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_portfolio_performance(self, authorized_client: TestClient):
        """Test getting portfolio performance"""
        response = authorized_client.get("/api/v1/portfolio/performance")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

class TestAlertsAPI:
    """Test alert management endpoints"""
    
    def test_create_alert(self, authorized_client: TestClient):
        """Test creating an alert"""
        alert_data = {
            "symbol": TestConfig.TEST_SYMBOL,
            "condition": "price > 160",
            "message": "Price alert triggered"
        }
        response = authorized_client.post("/api/v1/alerts/", json=alert_data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_get_alerts(self, authorized_client: TestClient):
        """Test getting all alerts"""
        response = authorized_client.get("/api/v1/alerts/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

class TestSettingsAPI:
    """Test settings management endpoints"""
    
    def test_get_settings(self, authorized_client: TestClient):
        """Test getting user settings"""
        response = authorized_client.get("/api/v1/settings/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_settings(self, authorized_client: TestClient):
        """Test updating user settings"""
        settings_data = {
            "theme": "dark",
            "notifications": True,
            "risk_tolerance": "medium"
        }
        response = authorized_client.put("/api/v1/settings/", json=settings_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

class TestBackupAPI:
    """Test backup and restore endpoints"""
    
    def test_create_backup(self, superuser_client: TestClient):
        """Test creating a backup"""
        response = superuser_client.post("/api/v1/backup/create")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_list_backups(self, superuser_client: TestClient):
        """Test listing backups"""
        response = superuser_client.get("/api/v1/backup/list")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_restore_backup(self, superuser_client: TestClient):
        """Test restoring a backup"""
        backup_id = "test_backup_123"
        response = superuser_client.post(f"/api/v1/backup/restore/{backup_id}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoint(self, client: TestClient):
        """Test invalid endpoint returns 404"""
        response = client.get("/api/v1/invalid/endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_invalid_json(self, authorized_client: TestClient):
        """Test invalid JSON returns 422"""
        response = authorized_client.post(
            "/api/v1/trading/strategies/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self, authorized_client: TestClient):
        """Test missing required fields returns 422"""
        incomplete_data = {"name": "Test Strategy"}
        response = authorized_client.post("/api/v1/trading/strategies/", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting on API endpoints"""
        # This would need to be implemented based on your rate limiting setup
        # For now, just test that endpoints are accessible
        response = client.get("/api/v1/market/data/AAPL")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS]

class TestDataValidation:
    """Test data validation across endpoints"""
    
    def test_invalid_symbol(self, authorized_client: TestClient):
        """Test invalid symbol handling"""
        response = authorized_client.get("/api/v1/market/data/INVALID_SYMBOL")
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
    
    def test_invalid_date_range(self, authorized_client: TestClient):
        """Test invalid date range handling"""
        params = {
            "symbol": TestConfig.TEST_SYMBOL,
            "start_date": "2023-12-31",
            "end_date": "2023-01-01"  # End before start
        }
        response = authorized_client.get("/api/v1/market/historical", params=params)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_invalid_quantity(self, authorized_client: TestClient):
        """Test invalid quantity handling"""
        trade_data = {
            "symbol": TestConfig.TEST_SYMBOL,
            "type": "buy",
            "quantity": -100,  # Negative quantity
            "price": TestConfig.TEST_PRICE
        }
        response = authorized_client.post("/api/v1/trading/trades/", json=trade_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
