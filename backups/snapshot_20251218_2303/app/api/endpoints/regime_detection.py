from fastapi import APIRouter, Body
from app.services.regime_detection import detect_market_regime
import pandas as pd

router = APIRouter()

@router.post("/regime/detect")
def regime_detect(prices: list = Body(...)):
    prices = pd.Series(prices)
    return detect_market_regime(prices).to_dict(orient='records') 