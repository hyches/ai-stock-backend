import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
AUTH_TOKEN = "your_valid_token_here"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {AUTH_TOKEN}"}

def test_ml_predict_valid_and_invalid_inputs():
    url = f"{BASE_URL}/api/v1/ml/predict"
    
    # Valid input example
    valid_payload = {
        "symbol": "AAPL",
        "features": {
            "feature1": 1.23,
            "feature2": 4.56
        }
    }
    
    # Invalid input examples (missing required 'symbol', symbol empty, or features wrong type)
    invalid_payloads = [
        {},  # completely empty
        {"features": {"feature1": 1.23}},  # missing symbol
        {"symbol": "", "features": {"feature1": 1.23}},  # empty symbol
        {"symbol": "AAPL", "features": "not an object"}  # features wrong type
    ]
    
    # Test valid input
    try:
        response = requests.post(url, json=valid_payload, headers=HEADERS, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = response.json()
        # Check that prediction result is present (assuming result key)
        assert "prediction" in data or "result" in data, "Response JSON should include prediction result"
    except requests.RequestException as e:
        assert False, f"RequestException for valid input: {e}"

    # Test invalid inputs
    for invalid_payload in invalid_payloads:
        try:
            response = requests.post(url, json=invalid_payload, headers=HEADERS, timeout=TIMEOUT)
            assert response.status_code == 400, f"Expected status 400 for payload {invalid_payload}, got {response.status_code}"
        except requests.RequestException as e:
            assert False, f"RequestException for invalid input {invalid_payload}: {e}"

test_ml_predict_valid_and_invalid_inputs()