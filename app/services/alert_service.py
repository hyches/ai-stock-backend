import logging
from typing import Dict, List, Optional
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db

    async def create_alert(self, alert: AlertCreate) -> Alert:
        """Create a new alert"""
        db_alert = Alert(**alert.dict())
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)

        # Send notifications
        await self._send_notifications(db_alert)
        return db_alert

    def get_alerts(
        self,
        level: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """Get alerts with filters"""
        query = self.db.query(Alert)

        if level:
            query = query.filter(Alert.level == level)
        if source:
            query = query.filter(Alert.source == source)
        if start_date:
            query = query.filter(Alert.created_at >= start_date)
        if end_date:
            query = query.filter(Alert.created_at <= end_date)

        return query.order_by(Alert.created_at.desc()).all()

    def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Get a single alert by ID"""
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def update_alert(self, alert_id: int, alert: AlertUpdate) -> Optional[Alert]:
        """Update an alert"""
        db_alert = self.get_alert(alert_id)
        if db_alert:
            for key, value in alert.dict(exclude_unset=True).items():
                setattr(db_alert, key, value)
            self.db.commit()
            self.db.refresh(db_alert)
        return db_alert

    async def _send_notifications(self, alert: Alert):
        """Send notifications for alert"""
        # Send webhook notification
        if settings.ALERT_WEBHOOK_URL:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        settings.ALERT_WEBHOOK_URL,
                        json={
                            "event": "alert",
                            "alert_id": alert.id,
                            "message": alert.message,
                            "level": alert.level,
                            "source": alert.source,
                            "metadata": alert.metadata,
                            "created_at": alert.created_at.isoformat()
                        }
                    )
            except Exception as e:
                logger.error(f"Error sending webhook notification: {str(e)}")

        # Send email notification for critical alerts
        if alert.level == "critical" and settings.ALERT_EMAIL:
            try:
                # Implement email sending logic here
                pass
            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")
