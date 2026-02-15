#!/usr/bin/env python
"""Quick test of the research endpoint fix"""
import asyncio
from app.api.endpoints.research import get_comprehensive_stock_data

async def test():
    try:
        print("Testing research endpoint with BEL.NS...")
        result = await get_comprehensive_stock_data("BEL.NS", period="3mo")
        print(f"✅ Success! Got data for {result.info.symbol}")
        print(f"   Result type: {type(result)}")
        print(f"   History type: {type(result.history)}")
        print(f"   History[0] type: {type(result.history[0])}")
        print(f"   History records: {len(result.history)}")
        print(f"   News records: {len(result.news)}")
        if result.history:
            h = result.history[0]
            print(f"   First history (type: {type(h).__name__}): date={h.date}, close={h.close}")
        if result.news:
            n = result.news[0]
            print(f"   First news (type: {type(n).__name__}): title={n.title}")
            print(f"   First news sentiment: {n.sentiment}")
            print(f"   First news relevance: {n.relevance_score}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
