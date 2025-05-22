import pytest
from fastapi.testclient import TestClient
from app.main import app
import jwt
from datetime import datetime, timedelta
from app.config.production import settings
import re
import asyncio

client = TestClient(app)

def test_jwt_token_validation():
    """Test JWT token validation"""
    # Create valid token
    valid_token = jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Create expired token
    expired_token = jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() - timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Create token with invalid signature
    invalid_token = jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=15)},
        "invalid_secret",
        algorithm=settings.ALGORITHM
    )
    
    # Test valid token
    response = client.get(
        "/api/stocks/AAPL/sentiment",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    
    # Test expired token
    response = client.get(
        "/api/stocks/AAPL/sentiment",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    
    # Test invalid token
    response = client.get(
        "/api/stocks/AAPL/sentiment",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401

def test_password_hashing():
    """Test password hashing and verification"""
    from app.core.security import get_password_hash, verify_password
    
    # Test password hashing
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Verify hash is different from plain text
    assert hashed != password
    
    # Verify password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_rate_limiting():
    """Test rate limiting"""
    # Get valid token
    response = client.post(
        "/api/auth/login",
        json={"username": "test@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make multiple requests to trigger rate limit
    for _ in range(6):  # Exceed auth rate limit
        response = client.post("/api/auth/login", headers=headers)
    
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]

def test_sql_injection():
    """Test SQL injection prevention"""
    # Test SQL injection in stock symbol
    response = client.get(
        "/api/stocks/AAPL'; DROP TABLE users; --/sentiment",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 404
    
    # Test SQL injection in portfolio name
    response = client.post(
        "/api/portfolios",
        json={
            "name": "Test'; DROP TABLE portfolios; --",
            "stocks": [{"symbol": "AAPL", "weight": 1.0}]
        },
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 422

def test_xss_prevention():
    """Test XSS prevention"""
    # Test XSS in portfolio name
    response = client.post(
        "/api/portfolios",
        json={
            "name": "<script>alert('xss')</script>",
            "stocks": [{"symbol": "AAPL", "weight": 1.0}]
        },
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 422
    
    # Test XSS in report content
    response = client.post(
        "/api/reports",
        json={
            "portfolio_id": 1,
            "report_type": "full_analysis",
            "format": "pdf",
            "content": "<script>alert('xss')</script>"
        },
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 422

def test_csrf_protection():
    """Test CSRF protection"""
    # Test without CSRF token
    response = client.post(
        "/api/portfolios",
        json={
            "name": "Test Portfolio",
            "stocks": [{"symbol": "AAPL", "weight": 1.0}]
        },
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 403
    
    # Test with invalid CSRF token
    response = client.post(
        "/api/portfolios",
        json={
            "name": "Test Portfolio",
            "stocks": [{"symbol": "AAPL", "weight": 1.0}]
        },
        headers={
            "Authorization": f"Bearer {get_test_token()}",
            "X-CSRF-Token": "invalid_token"
        }
    )
    assert response.status_code == 403

def test_security_headers():
    """Test security headers"""
    response = client.get("/health")
    
    # Check security headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers

@pytest.mark.asyncio
async def test_api_key_rotation():
    """Test API key rotation"""
    from app.core.security import api_key_manager
    
    # Get initial API key
    initial_key = await api_key_manager.get_api_key("news_api")
    
    # Rotate API key
    new_key = await api_key_manager.rotate_api_key("news_api")
    
    # Verify new key is different
    assert new_key != initial_key
    
    # Verify old key still works during grace period
    assert await api_key_manager.verify_api_key("news_api", initial_key)
    
    # Wait for grace period
    await asyncio.sleep(86400)  # 24 hours
    
    # Verify old key no longer works
    assert not await api_key_manager.verify_api_key("news_api", initial_key)

def test_input_validation():
    """Test input validation"""
    # Test invalid stock symbol
    response = client.get(
        "/api/stocks/INVALID_SYMBOL/sentiment",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 422
    
    # Test invalid portfolio weights
    response = client.post(
        "/api/portfolios",
        json={
            "name": "Test Portfolio",
            "stocks": [
                {"symbol": "AAPL", "weight": 2.0},  # Weight > 1
                {"symbol": "MSFT", "weight": -0.5}  # Negative weight
            ]
        },
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 422
    
    # Test invalid email format
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 422

def test_file_upload_security():
    """Test file upload security"""
    # Test file size limit
    large_file = b"x" * (10 * 1024 * 1024)  # 10MB
    response = client.post(
        "/api/reports/upload",
        files={"file": ("large.txt", large_file)},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 413
    
    # Test file type validation
    response = client.post(
        "/api/reports/upload",
        files={"file": ("script.js", b"alert('xss')")},
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 415

def get_test_token():
    """Helper function to get test token"""
    return jwt.encode(
        {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=15)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    ) 