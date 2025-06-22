from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_user
from app.services.market_data import get_stock_data, search_symbols
from app.schemas.market import StockData, SymbolSearch
from app.schemas.trading import PortfolioItem
from typing import List
import yfinance as yf

router = APIRouter()

@router.get("/portfolio", response_model=List[PortfolioItem])
def get_portfolio():
    """
    Retrieve portfolio with mock data.
    """
    # Mock data
    return [
        {
            "symbol": "AAPL",
            "shares": 10,
            "avgPrice": 150.0,
            "currentPrice": 175.25,
            "value": 1752.50,
            "change": 25.25,
            "changePercent": 1.44,
            "mlPrediction": { "direction": "up", "confidence": 0.88, "prediction": 180.50 }
        },
        {
            "symbol": "GOOGL",
            "shares": 5,
            "avgPrice": 2800.0,
            "currentPrice": 2850.75,
            "value": 14253.75,
            "change": -50.25,
            "changePercent": -0.35,
            "mlPrediction": { "direction": "down", "confidence": 0.92, "prediction": 2800.00 }
        }
    ]

@router.get("/watchlist/default", response_model=List[str])
def get_default_watchlist():
    """
    Retrieve default watchlist with mock data.
    """
    # Mock data
    return ["AAPL", "GOOGL", "MSFT", "TSLA"]

@router.get("/stock/{symbol}", response_model=StockData)
async def get_stock(
    symbol: str,
    interval: str = Query("1d", regex="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$"),
    current_user = Depends(get_current_user)
):
    try:
        data = await get_stock_data(symbol, interval)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching stock data: {str(e)}"
        )

@router.get("/search", response_model=List[SymbolSearch])
async def search(
    query: str = Query(..., min_length=1),
    current_user = Depends(get_current_user)
):
    try:
        results = await search_symbols(query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching symbols: {str(e)}"
        ) 