import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.models.database import User
from app.models.portfolio import Portfolio
from app.models.stock import Stock
from app.database import get_db
import jwt
from datetime import datetime, timedelta
from app.core.config import Settings

client = TestClient(app)
settings = Settings()

@pytest.fixture
def test_user():
    """Create a test user"""
    db = next(get_db())
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    """Create a test JWT token"""
    return jwt.encode(
        {"sub": test_user.email, "exp": datetime.utcnow() + timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

@pytest.fixture
def test_portfolio(test_user):
    """Create a test portfolio"""
    db = next(get_db())
    portfolio = Portfolio(
        name="Test Portfolio",
        user_id=test_user.id,
        stocks=[
            Stock(symbol="AAPL", weight=0.4),
            Stock(symbol="MSFT", weight=0.3),
            Stock(symbol="GOOGL", weight=0.3)
        ]
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio

def test_user_workflow(test_user, test_token):
    """Test complete user workflow"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # 1. Get user profile
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    
    # 2. Update user profile
    response = client.put(
        "/api/users/me",
        json={"full_name": "Updated Name"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    
    # 3. Change password
    response = client.put(
        "/api/users/me/password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123"
        },
        headers=headers
    )
    assert response.status_code == 200
    
    # 4. Login with new password
    response = client.post(
        "/api/auth/login",
        json={
            "username": test_user.email,
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_portfolio_workflow(test_user, test_token, test_portfolio):
    """Test complete portfolio workflow"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # 1. Get all portfolios
    response = client.get("/api/portfolios", headers=headers)
    assert response.status_code == 200
    portfolios = response.json()
    assert len(portfolios) == 1
    assert portfolios[0]["name"] == test_portfolio.name
    
    # 2. Get specific portfolio
    response = client.get(f"/api/portfolios/{test_portfolio.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == test_portfolio.name
    
    # 3. Update portfolio
    response = client.put(
        f"/api/portfolios/{test_portfolio.id}",
        json={
            "name": "Updated Portfolio",
            "stocks": [
                {"symbol": "AAPL", "weight": 0.5},
                {"symbol": "MSFT", "weight": 0.5}
            ]
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Portfolio"
    
    # 4. Create new portfolio
    response = client.post(
        "/api/portfolios",
        json={
            "name": "New Portfolio",
            "stocks": [
                {"symbol": "GOOGL", "weight": 0.6},
                {"symbol": "AMZN", "weight": 0.4}
            ]
        },
        headers=headers
    )
    assert response.status_code == 200
    new_portfolio_id = response.json()["id"]
    
    # 5. Delete portfolio
    response = client.delete(f"/api/portfolios/{new_portfolio_id}", headers=headers)
    assert response.status_code == 200

def test_stock_analysis_workflow(test_user, test_token):
    """Test complete stock analysis workflow"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # 1. Get stock sentiment
    response = client.get("/api/stocks/AAPL/sentiment", headers=headers)
    assert response.status_code == 200
    sentiment = response.json()
    assert "score" in sentiment
    assert "confidence" in sentiment
    
    # 2. Get stock news
    response = client.get("/api/stocks/AAPL/news", headers=headers)
    assert response.status_code == 200
    news = response.json()
    assert isinstance(news, list)
    assert len(news) > 0
    assert "title" in news[0]
    assert "url" in news[0]
    
    # 3. Get stock analysis
    response = client.get("/api/stocks/AAPL/analysis", headers=headers)
    assert response.status_code == 200
    analysis = response.json()
    assert "technical" in analysis
    assert "fundamental" in analysis
    assert "sentiment" in analysis

def test_report_generation_workflow(test_user, test_token, test_portfolio):
    """Test complete report generation workflow"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # 1. Generate report
    response = client.post(
        "/api/reports",
        json={
            "portfolio_id": test_portfolio.id,
            "report_type": "full_analysis",
            "format": "pdf"
        },
        headers=headers
    )
    assert response.status_code == 200
    report = response.json()
    assert "report_id" in report
    report_id = report["report_id"]
    
    # 2. Get report status
    response = client.get(f"/api/reports/{report_id}/status", headers=headers)
    assert response.status_code == 200
    status = response.json()
    assert "status" in status
    assert status["status"] in ["pending", "processing", "completed", "failed"]
    
    # 3. Download report
    response = client.get(f"/api/reports/{report_id}/download", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_error_handling_workflow(test_user, test_token):
    """Test error handling workflow"""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # 1. Test invalid stock symbol
    response = client.get("/api/stocks/INVALID/sentiment", headers=headers)
    assert response.status_code == 404
    assert "Stock not found" in response.json()["detail"]
    
    # 2. Test invalid portfolio ID
    response = client.get("/api/portfolios/999999", headers=headers)
    assert response.status_code == 404
    assert "Portfolio not found" in response.json()["detail"]
    
    # 3. Test invalid report ID
    response = client.get("/api/reports/999999/status", headers=headers)
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]
    
    # 4. Test invalid request body
    response = client.post(
        "/api/portfolios",
        json={
            "name": "Test Portfolio",
            "stocks": [
                {"symbol": "AAPL", "weight": 2.0}  # Invalid weight
            ]
        },
        headers=headers
    )
    assert response.status_code == 422
    assert "weight" in response.json()["detail"][0]["loc"]

def test_concurrent_operations(test_user, test_token):
    """Test concurrent operations"""
    import asyncio
    import aiohttp
    
    async def make_request(session, url, headers):
        async with session.get(url, headers=headers) as response:
            return await response.json()
    
    async def run_concurrent_requests():
        headers = {"Authorization": f"Bearer {test_token}"}
        urls = [
            "/api/stocks/AAPL/sentiment",
            "/api/stocks/MSFT/sentiment",
            "/api/stocks/GOOGL/sentiment"
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, f"{client.base_url}{url}", headers) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
    
    # Run concurrent requests
    results = asyncio.run(run_concurrent_requests())
    
    # Verify all requests were successful
    assert len(results) == 3
    for result in results:
        assert "score" in result
        assert "confidence" in result 