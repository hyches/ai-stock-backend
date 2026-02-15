from fastapi import APIRouter, HTTPException
from typing import Dict
from app.services.ml_predictions import ml_predictions

router = APIRouter()

@router.get("/{symbol}")
async def get_predictions(symbol: str) -> Dict:
    """
    Get ML predictions for a given symbol
    """
    try:
        predictions = await ml_predictions.get_comprehensive_predictions(symbol)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 