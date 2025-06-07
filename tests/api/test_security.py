import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    check_permissions
)

def test_create_access_token():
    """Test creating access token"""
    data = {"sub": "test@example.com", "permissions": ["view_strategies"]}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_verify_password():
    """Test password verification"""
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)

def test_check_permissions(authorized_client, test_user):
    """Test permission checking"""
    # Test with required permissions
    assert check_permissions(["view_strategies"])(test_user)
    
    # Test with missing permissions
    with pytest.raises(Exception):
        check_permissions(["manage_users"])(test_user)

def test_token_expiration(authorized_client):
    """Test token expiration"""
    # Create expired token
    expired_data = {
        "sub": "test@example.com",
        "permissions": ["view_strategies"],
        "exp": datetime.utcnow() - timedelta(minutes=1)
    }
    expired_token = create_access_token(expired_data)
    
    # Try to access endpoint with expired token
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_token(authorized_client):
    """Test invalid token"""
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_missing_token(authorized_client):
    """Test missing token"""
    response = authorized_client.get("/api/v1/trading/strategies/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_superuser_permissions(superuser_client):
    """Test superuser permissions"""
    # Superuser should have access to all endpoints
    endpoints = [
        "/api/v1/trading/strategies/",
        "/api/v1/trading/trades/",
        "/api/v1/trading/portfolios/",
        "/api/v1/trading/positions/",
        "/api/v1/trading/backtest/"
    ]
    
    for endpoint in endpoints:
        response = superuser_client.get(endpoint)
        assert response.status_code == status.HTTP_200_OK

def test_rate_limiting(authorized_client):
    """Test rate limiting"""
    # Make multiple requests in quick succession
    for _ in range(100):
        response = authorized_client.get("/api/v1/trading/strategies/")
    
    # The next request should be rate limited
    response = authorized_client.get("/api/v1/trading/strategies/")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

def test_cors_headers(authorized_client):
    """Test CORS headers"""
    response = authorized_client.options("/api/v1/trading/strategies/")
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_session_management(authorized_client):
    """Test session management"""
    # Create a session
    response = authorized_client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == status.HTTP_200_OK
    session_token = response.json()["access_token"]
    
    # Use session token
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Invalidate session
    response = authorized_client.post("/api/v1/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    
    # Try to use invalidated session
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_password_validation(authorized_client):
    """Test password validation"""
    # Test weak password
    response = authorized_client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "weak",
        "full_name": "New User"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test strong password
    response = authorized_client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "StrongP@ssw0rd123",
        "full_name": "New User"
    })
    assert response.status_code == status.HTTP_201_CREATED

def test_api_key_validation(authorized_client):
    """Test API key validation"""
    # Test missing API key
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"X-API-Key": ""}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test invalid API key
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test valid API key
    response = authorized_client.get(
        "/api/v1/trading/strategies/",
        headers={"X-API-Key": "test_api_key"}
    )
    assert response.status_code == status.HTTP_200_OK 