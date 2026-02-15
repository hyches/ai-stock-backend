import yfinance as yf
import sys

def test_options(symbol):
    print(f"Testing {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        options = ticker.options
        print(f"Options expirations: {options}")
        if options:
            chain = ticker.option_chain(options[0])
            print(f"First expiry calls: {len(chain.calls)}")
            print(f"First expiry puts: {len(chain.puts)}")
            if not chain.calls.empty:
                print("Sample Call:", chain.calls.iloc[0].to_dict())
        else:
            print("No options found.")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

symbols = ["^NSEI", "RELIANCE.NS", "TCS.NS", "NIFTY"]
for s in symbols:
    test_options(s)
