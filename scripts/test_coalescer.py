import asyncio
import time

from app.core.config import settings
from app.services.data_providers.yfinance_provider import YFinanceProvider
from app.services.request_coalescer import RequestCoalescer


async def run_test():
    # Use YFinanceProvider directly to avoid abstract provider instantiation issues
    provider = YFinanceProvider()
    coalescer = RequestCoalescer()
    symbol = "AAPL"
    limit = 5

    async def call_news(i):
        t0 = time.perf_counter()
        try:
            result = await coalescer.coalesce(f"news:{symbol}:{limit}", provider.get_news, symbol, limit)
            dt = time.perf_counter() - t0
            return (i, len(result) if result else 0, dt)
        except Exception as e:
            dt = time.perf_counter() - t0
            return (i, f"ERR:{e}", dt)

    # Warm single call to measure baseline
    print("Running baseline single call (direct provider)...")
    t0 = time.perf_counter()
    single = await provider.get_news(symbol, limit)
    baseline = time.perf_counter() - t0
    print(f"Baseline: got {len(single) if single else 0} items in {baseline:.2f}s")

    # Now run 6 concurrent calls that will be coalesced
    print("Running 6 concurrent calls to test coalescing...")
    t0 = time.perf_counter()
    tasks = [asyncio.create_task(call_news(i)) for i in range(6)]
    results = await asyncio.gather(*tasks)
    total = time.perf_counter() - t0

    for r in results:
        print(f"call {r[0]} -> items: {r[1]} time: {r[2]:.2f}s")

    print(f"Total time for 6 concurrent calls: {total:.2f}s (baseline: {baseline:.2f}s)")


if __name__ == '__main__':
    asyncio.run(run_test())
