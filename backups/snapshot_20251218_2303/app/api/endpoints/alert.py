from fastapi import APIRouter, Body
from app.services.alert_service import AlertService

router = APIRouter()
service = AlertService()

@router.post("/alert/create")
def create_alert(user_id: int = Body(...), message: str = Body(...), level: str = Body('info')):
    return service.create_alert(user_id, message, level)

@router.get("/alert/list/{user_id}")
def list_alerts(user_id: int):
    return service.get_alerts(user_id)

@router.post("/alert/read")
def mark_read(alert_id: int = Body(...)):
    return service.mark_as_read(alert_id) 