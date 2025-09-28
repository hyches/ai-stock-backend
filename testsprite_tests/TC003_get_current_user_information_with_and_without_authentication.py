import requests

BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/me"
TIMEOUT = 30

def test_get_current_user_info_with_and_without_authentication():
    user_email = "testuser_tc003@example.com"
    user_password = "StrongPass123"
    user_full_name = "Test User TC003"

    # Register a new user
    register_payload = {
        "email": user_email,
        "password": user_password,
        "full_name": user_full_name
    }

    # Ensure user cleanup is not needed since no delete endpoint specified
    # Step 1: Register user
    r = requests.post(REGISTER_URL, json=register_payload, timeout=TIMEOUT)
    assert r.status_code == 201, f"User registration failed with status {r.status_code}: {r.text}"

    try:
        # Step 2: Login with registered user to get access token
        login_payload = {
            "email": user_email,
            "password": user_password
        }
        r = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
        assert r.status_code == 200, f"Login failed with status {r.status_code}: {r.text}"
        token = r.json().get("access_token") or r.json().get("token")
        assert token is not None, "Access token not found in login response"

        auth_headers = {
            "Authorization": f"Bearer {token}"
        }

        # Step 3: Access /api/v1/auth/me with valid token, expect 200 and user info
        r = requests.get(ME_URL, headers=auth_headers, timeout=TIMEOUT)
        assert r.status_code == 200, f"Authorized request failed with status {r.status_code}: {r.text}"
        json_data = r.json()
        # Validate returned user info contains at least email and full_name or similar fields
        assert "email" in json_data, "User info missing 'email' field"
        assert json_data.get("email") == user_email, "Returned user email does not match registered email"

        # Step 4: Access /api/v1/auth/me without any auth header, expect 401 Unauthorized
        r = requests.get(ME_URL, timeout=TIMEOUT)
        assert r.status_code == 401, f"Unauthorized request expected 401 but got {r.status_code}"

        # Step 5: Access /api/v1/auth/me with invalid token, expect 401 Unauthorized
        invalid_headers = {
            "Authorization": "Bearer invalidtoken123"
        }
        r = requests.get(ME_URL, headers=invalid_headers, timeout=TIMEOUT)
        assert r.status_code == 401, f"Bad token request expected 401 but got {r.status_code}"

    finally:
        # No user deletion endpoint provided in PRD, cleanup not possible via API
        pass

test_get_current_user_info_with_and_without_authentication()