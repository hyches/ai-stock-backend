import pytest
from sqlalchemy.orm import Session
from app.services.alert_service import AlertService
from app.schemas.alert import AlertCreate, AlertUpdate

@pytest.mark.asyncio
async def test_create_alert(db: Session):
    alert_service = AlertService(db)
    alert_in = AlertCreate(message="Test alert", level="info")
    alert = await alert_service.create_alert(alert_in)
    assert alert.message == "Test alert"
    assert alert.level == "info"
    assert alert.id is not None

@pytest.mark.asyncio
async def test_get_alerts(db: Session):
    alert_service = AlertService(db)
    alert_in = AlertCreate(message="Test alert", level="info")
    await alert_service.create_alert(alert_in)
    alerts = alert_service.get_alerts()
    assert len(alerts) > 0

@pytest.mark.asyncio
async def test_get_alert(db: Session):
    alert_service = AlertService(db)
    alert_in = AlertCreate(message="Test alert", level="info")
    alert = await alert_service.create_alert(alert_in)
    retrieved_alert = alert_service.get_alert(alert.id)
    assert retrieved_alert.id == alert.id

@pytest.mark.asyncio
async def test_update_alert(db: Session):
    alert_service = AlertService(db)
    alert_in = AlertCreate(message="Test alert", level="info")
    alert = await alert_service.create_alert(alert_in)
    alert_update = AlertUpdate(read=True)
    updated_alert = alert_service.update_alert(alert.id, alert_update)
    assert updated_alert.read is True
