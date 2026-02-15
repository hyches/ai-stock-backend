from fastapi import APIRouter, Query
from app.services.forecasting import get_forecast

router = APIRouter()

@router.get("/forecast/{symbol}")
def forecast(symbol: str, model: str = Query('prophet'), days: int = Query(30)):
    return get_forecast(symbol, model, days) 