# app/api/endpoints/agents.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.trader import agent_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class StockAnalysisRequest(BaseModel):
    symbol: str

@router.post("/analyze")
async def analyze_stock_with_agents(request: StockAnalysisRequest):
    """
    Triggers a full multi-agent analysis for a given stock symbol.
    Uses Technical, Fundamental, and Sentiment agents.
    """
    try:
        result = await agent_service.run_full_analysis(request.symbol)
        return result
    except Exception as e:
        logger.error(f"Error in multi-agent analysis for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
