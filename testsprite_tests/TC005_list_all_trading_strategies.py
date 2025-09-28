import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_list_all_trading_strategies():
    url = f"{BASE_URL}/api/v1/trading/strategies/"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON"

    # Validate that the response is a list (or something iterable) representing strategies
    assert isinstance(data, list), f"Expected response to be a list but got {type(data)}"

    # Optional: Validate structure of one strategy if available
    if len(data) > 0:
        strategy = data[0]
        assert isinstance(strategy, dict), "Each strategy should be a JSON object"
        # Check at least some expected keys exist
        expected_keys = {"name", "strategy_type"}
        assert expected_keys.intersection(strategy.keys()), f"Strategy should have keys {expected_keys}"

test_list_all_trading_strategies()
