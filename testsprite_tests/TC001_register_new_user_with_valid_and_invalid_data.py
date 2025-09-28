import requests
import time

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/v1/auth/register"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30

def test_register_new_user_with_valid_and_invalid_data():
    timestamp = int(time.time())
    # Valid user registration data with unique email
    valid_payload = {
        "email": f"testuser_valid_{timestamp}@example.com",
        "password": "StrongPass123",
        "full_name": "Valid User"
    }

    # Invalid user registration data (missing required full_name and short password)
    invalid_payloads = [
        {
            "email": "testuser_invalid1@example.com",
            "password": "Short1"
            # full_name missing
        },
        {
            "email": "invalid-email-format",
            "password": "ValidPass123",
            "full_name": "Invalid Email User"
        },
        {
            # missing email
            "password": "ValidPass123",
            "full_name": "No Email User"
        }
    ]

    try:
        # Test valid registration - expect 201 Created
        response = requests.post(
            BASE_URL + REGISTER_ENDPOINT,
            json=valid_payload,
            headers=HEADERS,
            timeout=TIMEOUT
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code} with body {response.text}"

        # Test invalid registrations - expect 400 or 422 Bad Request
        for invalid_payload in invalid_payloads:
            r = requests.post(
                BASE_URL + REGISTER_ENDPOINT,
                json=invalid_payload,
                headers=HEADERS,
                timeout=TIMEOUT
            )
            assert r.status_code in (400, 422), f"Expected 400 or 422, got {r.status_code} for payload {invalid_payload} with body {r.text}"

    finally:
        # Cleanup: Attempt to delete the created user if the system supports it (not specified in PRD)
        # Since delete user API is not specified, we skip cleanup here.
        pass

test_register_new_user_with_valid_and_invalid_data()
