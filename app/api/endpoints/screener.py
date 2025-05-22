from fastapi import APIRouter, HTTPException
from typing import List
from app.models.stock import StockIn, StockOut
from app.services.screener import StockScreener

router = APIRouter()

@router.post("/screener", response_model=List[StockOut])
async def screen_stocks(criteria: StockIn):
    """
    Screen stocks based on provided criteria.
    
    Parameters:
    - sector: Filter by stock sector
    - min_volume: Minimum trading volume
    - max_pe: Maximum P/E ratio
    - min_market_cap: Minimum market capitalization
    - min_price: Minimum stock price
    - max_price: Maximum stock price
    - min_dividend_yield: Minimum dividend yield
    
    Returns:
    - List of stocks matching the criteria
    """
    try:
        screener = StockScreener()
        results = await screener.screen_stocks(criteria)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error screening stocks: {str(e)}"
        ) 