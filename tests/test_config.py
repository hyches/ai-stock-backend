"""
Test configuration and utilities for comprehensive testing
"""
import os
import pytest
import asyncio
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from unittest.mock import Mock, patch, AsyncMock

from app.main import app
from app.db.base_class import Base
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestConfig:
    """Test configuration constants"""
    
    # Test data constants
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "testpassword123"
    TEST_USER_FULL_NAME = "Test User"
    
    TEST_SUPERUSER_EMAIL = "admin@example.com"
    TEST_SUPERUSER_PASSWORD = "adminpassword123"
    TEST_SUPERUSER_FULL_NAME = "Admin User"
    
    # Test trading data
    TEST_SYMBOL = "AAPL"
    TEST_SYMBOL_2 = "GOOGL"
    TEST_PRICE = 150.0
    TEST_QUANTITY = 100
    TEST_INITIAL_BALANCE = 100000.0
    
    # Test strategy data
    TEST_STRATEGY_NAME = "Test Strategy"
    TEST_STRATEGY_TYPE = "trend_following"
    
    # Test portfolio data
    TEST_PORTFOLIO_NAME = "Test Portfolio"
    
    # API endpoints to test
    API_ENDPOINTS = {
        "auth": "/api/v1/auth",
        "market": "/api/v1/market",
        "ml": "/api/v1/ml",
        "settings": "/api/v1/settings",
        "backup": "/api/v1/backup",
        "portfolio": "/api/v1/portfolio",
        "trading": "/api/v1/trading",
        "research": "/api/v1/research",
        "alerts": "/api/v1/alerts",
        "anomaly_detection": "/api/v1/anomaly_detection",
        "automl": "/api/v1/automl",
        "event_impact": "/api/v1/event_impact",
        "explainability": "/api/v1/explainability",
        "forecasting": "/api/v1/forecasting",
        "live_data": "/api/v1/live_data",
        "optimizer": "/api/v1/optimizer",
        "regime_detection": "/api/v1/regime_detection",
        "reports": "/api/v1/reports",
        "screener": "/api/v1/screener",
        "zerodha": "/api/v1/zerodha"
    }
    
    # Test scenarios
    TEST_SCENARIOS = {
        "authentication": [
            "user_registration",
            "user_login",
            "token_validation",
            "password_reset",
            "user_logout"
        ],
        "trading": [
            "create_strategy",
            "update_strategy",
            "delete_strategy",
            "create_trade",
            "update_trade",
            "delete_trade",
            "create_portfolio",
            "update_portfolio",
            "delete_portfolio",
            "create_position",
            "update_position",
            "delete_position",
            "run_backtest",
            "get_backtest_results"
        ],
        "ml_services": [
            "ml_predictions",
            "model_training",
            "model_performance",
            "feature_importance",
            "batch_predictions"
        ],
        "market_data": [
            "fetch_market_data",
            "real_time_data",
            "historical_data",
            "technical_indicators",
            "market_screening"
        ],
        "portfolio_management": [
            "portfolio_creation",
            "portfolio_analysis",
            "risk_management",
            "performance_tracking",
            "rebalancing"
        ],
        "alerts_and_notifications": [
            "create_alert",
            "update_alert",
            "delete_alert",
            "trigger_alert",
            "alert_history"
        ],
        "data_management": [
            "data_backup",
            "data_restore",
            "data_validation",
            "data_cleaning",
            "data_export"
        ]
    }

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db() -> sessionmaker:
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db: sessionmaker) -> TestClient:
    """Create test client with test database"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def redis_client():
    """Create test Redis client"""
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    try:
        yield client
    finally:
        client.close()

@pytest.fixture(scope="module")
def test_user(db: sessionmaker) -> User:
    """Create test user"""
    user = User(
        email=TestConfig.TEST_USER_EMAIL,
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # testpassword123
        full_name=TestConfig.TEST_USER_FULL_NAME,
        is_active=True,
        is_superuser=False,
        permissions=["view_strategies", "manage_strategies", "view_trades", "manage_trades"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="module")
def test_superuser(db: sessionmaker) -> User:
    """Create test superuser"""
    user = User(
        email=TestConfig.TEST_SUPERUSER_EMAIL,
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # adminpassword123
        full_name=TestConfig.TEST_SUPERUSER_FULL_NAME,
        is_active=True,
        is_superuser=True,
        permissions=[]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="module")
def test_user_token(test_user: User) -> str:
    """Create test user token"""
    return create_access_token(
        data={"sub": test_user.id, "permissions": test_user.permissions}
    )

@pytest.fixture(scope="module")
def test_superuser_token(test_superuser: User) -> str:
    """Create test superuser token"""
    return create_access_token(
        data={"sub": test_superuser.id, "permissions": []}
    )

@pytest.fixture(scope="module")
def authorized_client(client: TestClient, test_user_token: str) -> TestClient:
    """Create authorized test client"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_user_token}"
    }
    return client

@pytest.fixture(scope="module")
def superuser_client(client: TestClient, test_superuser_token: str) -> TestClient:
    """Create superuser test client"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_superuser_token}"
    }
    return client

# Test data fixtures
@pytest.fixture
def sample_strategy_data() -> Dict[str, Any]:
    """Sample strategy data for testing"""
    return {
        "name": TestConfig.TEST_STRATEGY_NAME,
        "description": "Test strategy description",
        "type": TestConfig.TEST_STRATEGY_TYPE,
        "parameters": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }
    }

@pytest.fixture
def sample_trade_data() -> Dict[str, Any]:
    """Sample trade data for testing"""
    return {
        "symbol": TestConfig.TEST_SYMBOL,
        "type": "buy",
        "quantity": TestConfig.TEST_QUANTITY,
        "price": TestConfig.TEST_PRICE
    }

@pytest.fixture
def sample_portfolio_data() -> Dict[str, Any]:
    """Sample portfolio data for testing"""
    return {
        "name": TestConfig.TEST_PORTFOLIO_NAME,
        "description": "Test portfolio description",
        "initial_balance": TestConfig.TEST_INITIAL_BALANCE
    }

@pytest.fixture
def sample_ml_data() -> Dict[str, Any]:
    """Sample ML prediction data for testing"""
    return {
        "f0": 0.1, "f1": 0.2, "f2": 0.3, "f3": 0.4, "f4": 0.5,
        "f5": 0.6, "f6": 0.7, "f7": 0.8, "f8": 0.9, "f9": 1.0
    }

@pytest.fixture
def sample_market_data() -> Dict[str, Any]:
    """Sample market data for testing"""
    return {
        "symbol": TestConfig.TEST_SYMBOL,
        "open": 149.0,
        "high": 152.0,
        "low": 148.0,
        "close": 151.0,
        "volume": 1000000,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Mock fixtures for external services
@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch('redis.Redis') as mock:
        mock_instance = Mock()
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.delete.return_value = True
        mock_instance.exists.return_value = False
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_yfinance():
    """Mock yfinance for market data"""
    with patch('yfinance.Ticker') as mock:
        mock_instance = Mock()
        mock_instance.history.return_value = Mock()
        mock_instance.info = {
            'currentPrice': 150.0,
            'marketCap': 2500000000000,
            'volume': 1000000
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_ml_model():
    """Mock ML model for testing"""
    with patch('app.services.ml_service.ml_model') as mock:
        mock.predict.return_value = 1
        mock.batch_predict.return_value = [1, 0, 1]
        mock.get_performance.return_value = {
            'accuracy': 0.85,
            'loss': 0.3
        }
        mock.get_feature_importance.return_value = {
            'f0': 0.1, 'f1': 0.2, 'f2': 0.15
        }
        yield mock
