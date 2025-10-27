from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.alert import Alert, AlertCreate, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter()

@router.post("/", response_model=Alert)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(deps.get_db),
):
    """
    Create new alert.
    """
    alert_service = AlertService(db)
    return await alert_service.create_alert(alert=alert)

@router.get("/", response_model=List[Alert])
def read_alerts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve alerts.
    """
    alert_service = AlertService(db)
    alerts = alert_service.get_alerts(skip=skip, limit=limit)
    return alerts

@router.get("/{alert_id}", response_model=Alert)
def read_alert(
    alert_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Get alert by ID.
    """
    alert_service = AlertService(db)
    db_alert = alert_service.get_alert(alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

@router.put("/{alert_id}", response_model=Alert)
def update_alert(
    alert_id: int,
    alert: AlertUpdate,
    db: Session = Depends(deps.get_db),
):
    """
    Update an alert.
    """
    alert_service = AlertService(db)
    db_alert = alert_service.update_alert(alert_id=alert_id, alert=alert)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert
