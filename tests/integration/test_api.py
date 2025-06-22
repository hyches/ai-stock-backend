import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import jwt
from datetime import datetime, timedelta
from app.core.config import Settings
from app.main import app
from app.database import Base, get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

settings = Settings()

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def auth_headers():
    def create_token():
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode = {"sub": "testuser", "exp": expire}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return {"Authorization": f"Bearer {create_token()}"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_db_health_check(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"

def test_cache_health_check(client):
    response = client.get("/health/cache")
    assert response.status_code == 200
    assert response.json()["cache"] == "connected"

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "memory_usage" in response.json()
    assert "cpu_usage" in response.json()
    assert "disk_usage" in response.json()

def test_rate_limiting(client, auth_headers):
    # Make multiple requests to trigger rate limit
    for _ in range(6):  # Exceed auth rate limit
        response = client.post("/api/auth/login", headers=auth_headers)
    
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]

def test_stock_analysis(client, auth_headers):
    response = client.get("/api/stocks/AAPL/sentiment", headers=auth_headers)
    assert response.status_code == 200
    assert "overall_score" in response.json()
    assert "news_sentiment" in response.json()
    assert "social_sentiment" in response.json()

def test_competitor_analysis(client, auth_headers):
    response = client.get("/api/stocks/AAPL/competitors", headers=auth_headers)
    assert response.status_code == 200
    assert "competitors" in response.json()
    assert "market_position" in response.json()

def test_portfolio_creation(client, auth_headers):
    portfolio_data = {
        "name": "Test Portfolio",
        "stocks": [
            {"symbol": "AAPL", "weight": 0.4},
            {"symbol": "MSFT", "weight": 0.3},
            {"symbol": "GOOGL", "weight": 0.3}
        ]
    }
    response = client.post("/api/portfolios", json=portfolio_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Portfolio"
    assert len(response.json()["stocks"]) == 3

def test_portfolio_optimization(client, auth_headers):
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio",
        "stocks": [
            {"symbol": "AAPL", "weight": 0.4},
            {"symbol": "MSFT", "weight": 0.3},
            {"symbol": "GOOGL", "weight": 0.3}
        ]
    }
    portfolio = client.post("/api/portfolios", json=portfolio_data, headers=auth_headers)
    portfolio_id = portfolio.json()["id"]
    
    # Then optimize it
    optimization_data = {
        "risk_tolerance": "moderate",
        "investment_horizon": "long_term",
        "constraints": {
            "max_weight": 0.4,
            "min_weight": 0.1
        }
    }
    response = client.post(
        f"/api/portfolios/{portfolio_id}/optimize",
        json=optimization_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "optimized_weights" in response.json()
    assert "expected_return" in response.json()
    assert "risk_score" in response.json()

def test_report_generation(client, auth_headers):
    # First create a portfolio
    portfolio_data = {
        "name": "Test Portfolio",
        "stocks": [
            {"symbol": "AAPL", "weight": 0.4},
            {"symbol": "MSFT", "weight": 0.3},
            {"symbol": "GOOGL", "weight": 0.3}
        ]
    }
    portfolio = client.post("/api/portfolios", json=portfolio_data, headers=auth_headers)
    portfolio_id = portfolio.json()["id"]
    
    # Generate report
    report_data = {
        "portfolio_id": portfolio_id,
        "report_type": "full_analysis",
        "format": "pdf"
    }
    response = client.post("/api/reports", json=report_data, headers=auth_headers)
    assert response.status_code == 200
    assert "report_id" in response.json()
    assert "download_url" in response.json()

def test_error_handling(client, auth_headers):
    # Test invalid stock symbol
    response = client.get("/api/stocks/INVALID/sentiment", headers=auth_headers)
    assert response.status_code == 404
    assert "Stock not found" in response.json()["detail"]
    
    # Test invalid portfolio ID
    response = client.get("/api/portfolios/999", headers=auth_headers)
    assert response.status_code == 404
    assert "Portfolio not found" in response.json()["detail"]
    
    # Test invalid report type
    report_data = {
        "portfolio_id": 1,
        "report_type": "invalid_type",
        "format": "pdf"
    }
    response = client.post("/api/reports", json=report_data, headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid report type" in response.json()["detail"]

def test_security_headers(client):
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers 