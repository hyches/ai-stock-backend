import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_historical_market_data_with_valid_symbol_and_period():
    url = f"{BASE_URL}/api/v1/market/historical"
    # Use a commonly known valid symbol and a valid period (optional)
    params = {
        "symbol": "AAPL",
        "period": "1mo"
    }
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"
    # Validate response status code
    assert response.status_code == 200
    # Validate response content structure contains expected keys for historical data
    data = response.json()
    assert isinstance(data, dict), "Response JSON should be an object"
    # Basic validations on returned data structure, expecting e.g. list of data points or dict with history info
    # Checking for presence of 'symbol' and 'historical' keys typically in historical market data
    assert "symbol" in data or "historical" in data or len(data) > 0, "Response should contain historical data attributes"

test_get_historical_market_data_with_valid_symbol_and_period()