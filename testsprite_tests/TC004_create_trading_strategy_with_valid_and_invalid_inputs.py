import requests

BASE_URL = "http://localhost:8000"
STRATEGIES_ENDPOINT = f"{BASE_URL}/api/v1/trading/strategies/"
AUTH_REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/auth/register"
AUTH_LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
TIMEOUT = 30


def get_auth_token():
    # Register a test user
    test_user = {
        "email": "testuser@example.com",
        "password": "StrongPassword123",
        "full_name": "Test User"
    }

    headers = {"Content-Type": "application/json"}

    # Attempt to register user; ignore if already exists
    try:
        requests.post(AUTH_REGISTER_ENDPOINT, json=test_user, headers=headers, timeout=TIMEOUT)
    except requests.RequestException:
        pass  # ignore registration failure here

    # Login to get token
    try:
        response_login = requests.post(
            AUTH_LOGIN_ENDPOINT,
            json={"email": test_user["email"], "password": test_user["password"]},
            headers=headers,
            timeout=TIMEOUT
        )
        response_login.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    login_data = response_login.json()
    token = login_data.get("access_token") or login_data.get("token")
    assert token is not None, "Authentication token not found in login response"
    return token


def test_create_trading_strategy_with_valid_and_invalid_inputs():
    token = get_auth_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Valid input data for creating a trading strategy
    valid_strategy_payload = {
        "name": "Mean Reversion Strategy",
        "description": "A strategy based on price reverting to mean",
        "strategy_type": "mean_reversion",
        "parameters": {
            "lookback_period": 20,
            "entry_threshold": 0.05,
            "exit_threshold": 0.02
        }
    }

    # Invalid input data (missing required 'strategy_type' field)
    invalid_strategy_payload = {
        "name": "Invalid Strategy",
        "description": "Missing strategy_type field"
        # strategy_type is required but omitted
    }

    # Test creating strategy with valid inputs
    try:
        response_valid = requests.post(
            STRATEGIES_ENDPOINT,
            json=valid_strategy_payload,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request failed for valid input: {e}"

    assert response_valid.status_code == 201, (
        f"Expected status code 201 for valid input, got {response_valid.status_code}, "
        f"response: {response_valid.text}"
    )
    created_strategy = response_valid.json()
    assert "name" in created_strategy and created_strategy["name"] == valid_strategy_payload["name"], \
        "Created strategy name does not match input"
    assert "strategy_type" in created_strategy and created_strategy["strategy_type"] == valid_strategy_payload["strategy_type"], \
        "Created strategy_type does not match input"

    # Test creating strategy with invalid inputs
    try:
        response_invalid = requests.post(
            STRATEGIES_ENDPOINT,
            json=invalid_strategy_payload,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request failed for invalid input: {e}"

    assert response_invalid.status_code == 400, (
        f"Expected status code 400 for invalid input, got {response_invalid.status_code}, "
        f"response: {response_invalid.text}"
    )


test_create_trading_strategy_with_valid_and_invalid_inputs()
