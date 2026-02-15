import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.zerodha import ZerodhaToken
from app.services.zerodha_service import ZerodhaService

logger = logging.getLogger(__name__)

class TokenRefreshService:
    def __init__(self):
        self.zerodha_service = ZerodhaService()
        self.refresh_threshold = timedelta(hours=1)  # Refresh 1 hour before expiry

    async def check_and_refresh_token(self) -> Optional[ZerodhaToken]:
        """Check token expiry and refresh if needed"""
        db = SessionLocal()
        try:
            token = db.query(ZerodhaToken).order_by(ZerodhaToken.created_at.desc()).first()
            if not token:
                logger.error("No token found")
                return None

            if self._should_refresh_token(token):
                new_token = await self._refresh_token(token)
                if new_token:
                    await self._notify_token_refresh(new_token)
                return new_token

            return token
        finally:
            db.close()

    def _should_refresh_token(self, token: ZerodhaToken) -> bool:
        """Check if token needs refresh"""
        return datetime.utcnow() + self.refresh_threshold >= token.expires_at

    async def _refresh_token(self, old_token: ZerodhaToken) -> Optional[ZerodhaToken]:
        """Refresh the token"""
        try:
            # Get new token from Zerodha
            new_token_data = self.zerodha_service.kite.renew_access_token(
                old_token.access_token,
                settings.ZERODHA_API_SECRET
            )

            # Create new token record
            db = SessionLocal()
            try:
                new_token = ZerodhaToken(
                    access_token=new_token_data["access_token"],
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                db.add(new_token)
                db.commit()
                return new_token
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None

    async def _notify_token_refresh(self, token: ZerodhaToken):
        """Send webhook notification about token refresh"""
        if not settings.ALERT_WEBHOOK_URL:
            return

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    settings.ALERT_WEBHOOK_URL,
                    json={
                        "event": "token_refresh",
                        "token_id": token.id,
                        "expires_at": token.expires_at.isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")

token_refresh_service = TokenRefreshService() 