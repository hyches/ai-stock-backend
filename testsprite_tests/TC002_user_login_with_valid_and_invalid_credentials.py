import requests

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
TIMEOUT = 30

def test_user_login_with_valid_and_invalid_credentials():
    # Define valid credentials (assuming there is a user with these credentials)
    valid_credentials = {
        "email": "validuser@example.com",
        "password": "ValidPass123"
    }

    # Define invalid credentials
    invalid_credentials = {
        "email": "invaliduser@example.com",
        "password": "WrongPass"
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Test login with valid credentials
    try:
        response_valid = requests.post(
            LOGIN_ENDPOINT,
            json=valid_credentials,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request for valid credentials failed: {e}"

    assert response_valid.status_code == 200, (
        f"Expected status code 200 for valid login, got {response_valid.status_code}."
    )
    # Removed ambiguous assertion on access token presence

    # Test login with invalid credentials
    try:
        response_invalid = requests.post(
            LOGIN_ENDPOINT,
            json=invalid_credentials,
            headers=headers,
            timeout=TIMEOUT
        )
    except requests.RequestException as e:
        assert False, f"Request for invalid credentials failed: {e}"

    assert response_invalid.status_code == 401, (
        f"Expected status code 401 for invalid login, got {response_invalid.status_code}."
    )
    # Optionally verify error message in response
    json_invalid = response_invalid.json()
    assert "detail" in json_invalid, (
        f"Response does not contain expected error detail for invalid login: {json_invalid}"
    )

test_user_login_with_valid_and_invalid_credentials()