from fastapi import APIRouter, Body
from app.services.anomaly_detection import detect_anomalies

router = APIRouter()

@router.post("/anomaly/detect")
def anomaly_detect(price_series: list = Body(...), volume_series: list = Body(...)):
    return detect_anomalies(price_series, volume_series).to_dict(orient='records') 