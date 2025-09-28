import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {
    "Accept": "application/json"
}

def test_get_market_data_existing_and_non_existing_symbol():
    # Known existing symbol (commonly used symbol for tests)
    existing_symbol = "AAPL"
    url_existing = f"{BASE_URL}/api/v1/market/data/{existing_symbol}"

    # Non-existing symbol (assumed)
    non_existing_symbol = "ZZZZZZ"
    url_non_existing = f"{BASE_URL}/api/v1/market/data/{non_existing_symbol}"

    # Test existing symbol - expect 200 and valid market data
    try:
        resp_existing = requests.get(url_existing, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to get existing symbol market data failed: {e}"

    assert resp_existing.status_code == 200, f"Expected 200 for existing symbol, got {resp_existing.status_code}"
    try:
        data = resp_existing.json()
    except ValueError:
        assert False, "Response for existing symbol is not a valid JSON"

    # Minimal validation for market data response content, expect some keys
    assert isinstance(data, dict), "Market data response should be a JSON object"
    # Check for presence of typical market data fields (stock symbol, price or similar)
    assert "symbol" in data or "Symbol" in data, "Market data missing 'symbol' key"
    
    # Test non-existing symbol - expect 404
    try:
        resp_non_existing = requests.get(url_non_existing, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to get non-existing symbol market data failed: {e}"

    assert resp_non_existing.status_code == 404, f"Expected 404 for non-existing symbol, got {resp_non_existing.status_code}"

test_get_market_data_existing_and_non_existing_symbol()