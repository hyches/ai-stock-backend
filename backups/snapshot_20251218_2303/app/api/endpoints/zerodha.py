from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.services.zerodha_service import ZerodhaService
from app.schemas.zerodha import (
    PaperTradeCreate,
    PaperTradeResponse,
    HistoricalDataRequest,
    HistoricalDataResponse
)

router = APIRouter()
zerodha_service = ZerodhaService()

@router.get("/login")
async def get_login_url():
    """Get Zerodha login URL"""
    return {"login_url": await zerodha_service.get_login_url()}

@router.get("/callback")
async def handle_callback(request_token: str):
    """Handle Zerodha callback with request token"""
    try:
        session_data = await zerodha_service.generate_session(request_token)
        return {"message": "Authentication successful", "data": session_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/historical-data")
async def get_historical_data(
    request: HistoricalDataRequest
) -> List[HistoricalDataResponse]:
    """Get historical OHLC data"""
    try:
        data = await zerodha_service.get_historical_data(
            request.instrument_token,
            request.from_date,
            request.to_date,
            request.interval
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/paper-trade", response_model=PaperTradeResponse)
async def place_paper_trade(trade: PaperTradeCreate):
    """Place a paper trade"""
    try:
        result = await zerodha_service.place_paper_trade(
            trade.symbol,
            trade.action,
            trade.quantity,
            trade.price
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/paper-portfolio", response_model=List[PaperTradeResponse])
async def get_paper_portfolio():
    """Get paper trading portfolio"""
    try:
        return await zerodha_service.get_paper_portfolio()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/paper-pnl")
async def get_paper_pnl():
    """Get paper trading PnL"""
    try:
        return await zerodha_service.calculate_pnl()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 