from nsepython import nse_optionchain_scrapper
import json

def test_nse_options(symbol):
    print(f"Testing NSE data for {symbol}...")
    try:
        data = nse_optionchain_scrapper(symbol)
        print("Data fetched successfully.")
        
        # Verify structure
        if 'records' in data and 'data' in data['records']:
            records = data['records']['data']
            print(f"Found {len(records)} combined records")
            if records:
                print("Sample Record:", json.dumps(records[0], indent=2))
        else:
            print("Data fetched but unexpected structure.")
            print(str(data)[:200])
            
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    print("-" * 20)

symbols = ["NIFTY", "BANKNIFTY", "RELIANCE", "TCS"]
for s in symbols:
    test_nse_options(s)
