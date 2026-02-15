from fastapi import APIRouter, Body
from app.services.event_impact import event_impact

router = APIRouter()

@router.post("/event/impact")
def event_impact_endpoint(symbol: str = Body(...), event_dates: list = Body(...)):
    return event_impact(symbol, event_dates) 