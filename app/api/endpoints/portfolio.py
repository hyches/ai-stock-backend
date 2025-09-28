from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User
from typing import Dict, Any

router = APIRouter()

@router.get("/")
def get_portfolio(current_user: User = Depends(get_current_user)):
    # Mock data
    return {
        "items": [
            {"symbol": "AAPL", "shares": 10, "avgPrice": 150.0, "currentPrice": 175.0, "totalValue": 1750.0, "change": 25.0, "changePercent": 16.67},
            {"symbol": "GOOGL", "shares": 5, "avgPrice": 2800.0, "currentPrice": 2850.0, "totalValue": 14250.0, "change": 50.0, "changePercent": 1.78},
        ],
        "totalValue": 16000.0,
        "totalChange": 75.0,
        "totalChangePercent": 0.47
    } 