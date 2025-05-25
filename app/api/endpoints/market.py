from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_user
from app.services.market_data import get_stock_data, search_symbols
from app.schemas.market import StockData, SymbolSearch
from typing import List
import yfinance as yf

router = APIRouter()

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