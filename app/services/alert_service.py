import logging
from typing import Dict, List, Optional
import httpx
from datetime import datetime
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.alert import Alert

logger = logging.getLogger(__name__)

class AlertService:
    """
    AlertService class to manage alerts and send notifications.
    Parameters:
        - message (str): Description of the alert.
        - level (str): Severity of the alert, optional, default is "info".
        - source (str): Origin of the alert, optional, default is "system".
        - metadata (Optional[Dict]): Additional data for the alert, optional.
    Processing Logic:
        - Ensures the alert level is valid; defaults to "info" if not specified.
        - Adds alert to database and commits the transaction.
        - Sends notifications through webhooks and emails for critical alerts.
        - Filters alerts based on level, source, and date parameters.
    """
    def __init__(self):
        self.alert_levels = {
            "info": "INFO",
            "warning": "WARNING",
            "error": "ERROR",
            "critical": "CRITICAL"
        }

    async def create_alert(
        self,
        message: str,
        level: str = "info",
        source: str = "system",
        metadata: Optional[Dict] = None
    ) -> Alert:
        """Create a new alert"""
        if level not in self.alert_levels:
            level = "info"

        db = SessionLocal()
        try:
            alert = Alert(
                message=message,
                level=level,
                source=source,
                metadata=metadata or {}
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)

            # Send notifications
            await self._send_notifications(alert)
            return alert
        finally:
            db.close()

    async def get_alerts(
        self,
        level: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """Get alerts with filters"""
        db = SessionLocal()
        try:
            query = db.query(Alert)
            
            if level:
                query = query.filter(Alert.level == level)
            if source:
                query = query.filter(Alert.source == source)
            if start_date:
                query = query.filter(Alert.created_at >= start_date)
            if end_date:
                query = query.filter(Alert.created_at <= end_date)
            
            return query.order_by(Alert.created_at.desc()).all()
        finally:
            db.close()

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

alert_service = AlertService() 