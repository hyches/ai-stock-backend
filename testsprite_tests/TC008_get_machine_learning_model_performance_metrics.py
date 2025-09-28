import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Placeholder for a valid token; replace with actual token when available
AUTH_TOKEN = "your_valid_token_here"

def test_get_ml_model_performance_metrics():
    url = f"{BASE_URL}/api/v1/ml/performance"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(data, dict), "Response JSON should be a dictionary"
    # Basic checks for expected keys in ML performance metrics - keys may vary; check for common metrics:
    expected_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    found_key = False
    for key in expected_keys:
        if key in data:
            found_key = True
            value = data[key]
            assert isinstance(value, (int, float)), f"Metric {key} should be numeric"
    assert found_key, f"Response JSON does not contain expected ML performance metrics keys: {expected_keys}"

test_get_ml_model_performance_metrics()