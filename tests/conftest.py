import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from app.main import app
from app.db.base_class import Base
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test database session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db: TestingSessionLocal) -> Generator:
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
def redis_client() -> Generator:
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
def test_user(db: TestingSessionLocal) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        permissions=["view_strategies", "manage_strategies"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="module")
def test_superuser(db: TestingSessionLocal) -> User:
    """Create test superuser"""
    user = User(
        email="admin@example.com",
        hashed_password="hashed_password",
        full_name="Admin User",
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

@pytest.fixture(scope="module")
def test_strategy(db: TestingSessionLocal, test_user: User) -> Dict:
    """Create test strategy"""
    strategy = {
        "name": "Test Strategy",
        "description": "Test strategy description",
        "type": "trend_following",
        "parameters": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        },
        "owner_id": test_user.id
    }
    return strategy

@pytest.fixture(scope="module")
def test_portfolio(db: TestingSessionLocal, test_user: User) -> Dict:
    """Create test portfolio"""
    portfolio = {
        "name": "Test Portfolio",
        "description": "Test portfolio description",
        "initial_balance": 100000.0,
        "owner_id": test_user.id
    }
    return portfolio

@pytest.fixture(scope="module")
def test_trade(db: TestingSessionLocal, test_user: User) -> Dict:
    """Create test trade"""
    trade = {
        "symbol": "AAPL",
        "type": "buy",
        "quantity": 100,
        "price": 150.0,
        "user_id": test_user.id
    }
    return trade

@pytest.fixture(scope="module")
def test_position(db: TestingSessionLocal, test_user: User) -> Dict:
    """Create test position"""
    position = {
        "symbol": "AAPL",
        "quantity": 100,
        "entry_price": 150.0,
        "current_price": 155.0,
        "user_id": test_user.id
    }
    return position

@pytest.fixture(scope="module")
def test_backtest(db: TestingSessionLocal, test_user: User) -> Dict:
    """Create test backtest"""
    backtest = {
        "strategy_id": 1,
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_balance": 100000.0,
        "user_id": test_user.id
    }
    return backtest 