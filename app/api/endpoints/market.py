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
    """Fetch stock data for a given symbol and interval.
    Parameters:
        - symbol (str): Ticker symbol of the stock.
        - interval (str, optional): Time interval for stock data aggregation. Default is "1d". Valid options are "1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo".
        - current_user: Obtained using dependency injection to ensure the request is made by an authenticated user.
    Returns:
        - dict: A dictionary containing stock data based on the specified symbol and interval.
    Processing Logic:
        - Validates the 'interval' parameter using a regex pattern to ensure correct format.
        - Utilizes asynchronous function to fetch stock data.
        - Handles exceptions by returning an HTTP error response with a 400 status code and an error detail if the stock data fetch operation fails."""
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
    """Search for symbols based on the provided query.
    Parameters:
        - query (str): The search query string. Must be at least 1 character long.
        - current_user: The current user performing the search, resolved via dependency injection.
    Returns:
        - list: A list of search results matching the query.
    Processing Logic:
        - Raises an HTTPException with a status code 400 if an error occurs during the search operation."""
    try:
        results = await search_symbols(query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching symbols: {str(e)}"
        ) 