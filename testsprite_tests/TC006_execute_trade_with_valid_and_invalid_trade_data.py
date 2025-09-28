import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def get_auth_token(email, password):
    url = f"{BASE_URL}/api/v1/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload, timeout=TIMEOUT)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("access_token")
    assert token is not None, "No access token in login response"
    return token


def test_execute_trade_with_valid_and_invalid_data():
    # Obtain auth token
    # Using test user credentials, they must exist in the test environment
    email = "testuser@example.com"
    password = "testpassword"
    token = get_auth_token(email, password)

    url = f"{BASE_URL}/api/v1/trading/trades/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Valid trade data
    valid_trade_payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.0,
        "trade_type": "buy"
    }

    # Invalid trade data (missing required 'trade_type')
    invalid_trade_payload = {
        "symbol": "AAPL",
        "quantity": 10,
        "price": 150.0
        # "trade_type" missing
    }

    # Test valid trade execution
    response = requests.post(url, json=valid_trade_payload, headers=headers, timeout=TIMEOUT)
    try:
        assert response.status_code == 201, f"Expected 201 for valid trade, got {response.status_code}"
    except AssertionError:
        # If the returned status is not 201, dump response content for diagnostics
        raise AssertionError(f"Response content: {response.text}")

    # Test invalid trade execution
    response_invalid = requests.post(url, json=invalid_trade_payload, headers=headers, timeout=TIMEOUT)
    try:
        assert response_invalid.status_code == 400, f"Expected 400 for invalid trade, got {response_invalid.status_code}"
    except AssertionError:
        raise AssertionError(f"Response content: {response_invalid.text}")


test_execute_trade_with_valid_and_invalid_data()