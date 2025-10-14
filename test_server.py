#!/usr/bin/env python3
"""
Test server to verify API endpoints work
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Stock Trading System Test", version="0.1.0")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Trading System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-trading-backend"}

@app.get("/api/v1/market/search")
def search_stocks(q: str = "AAPL"):
    """Test stock search endpoint"""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "type": "Stock"
        },
        {
            "symbol": "MSFT", 
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "type": "Stock"
        }
    ]

@app.get("/api/v1/market/data/{symbol}")
def get_stock_data(symbol: str):
    """Test stock data endpoint"""
    return {
        "symbol": symbol.upper(),
        "name": f"{symbol.upper()} Corporation",
        "price": 150.0,
        "change": 2.5,
        "changePercent": 1.69,
        "volume": 1000000,
        "marketCap": 2500000000000,
        "pe": 25.0,
        "eps": 6.0,
        "dividend": 0.96,
        "dividendYield": 0.64,
        "high52Week": 200.0,
        "low52Week": 120.0,
        "avgVolume": 50000000,
        "beta": 1.2,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "description": f"This is a test description for {symbol.upper()}.",
        "website": f"https://www.{symbol.lower()}.com",
        "employees": 150000,
        "founded": 1976,
        "headquarters": "Cupertino, CA, USA"
    }

if __name__ == "__main__":
    print("🚀 Starting Test Server...")
    print("🌐 Server URL: http://127.0.0.1:8000")
    print("📊 Health Check: http://127.0.0.1:8000/health")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

