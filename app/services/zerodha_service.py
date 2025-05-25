from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from kiteconnect import KiteConnect, KiteTicker
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.zerodha import ZerodhaToken, PaperTrade

logger = logging.getLogger(__name__)

class ZerodhaService:
    def __init__(self):
        self.kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
        self.kws = None
        self._setup_websocket()

    def _setup_websocket(self):
        """Setup WebSocket connection for real-time data"""
        try:
            self.kws = KiteTicker(settings.ZERODHA_API_KEY, self._get_access_token())
            self.kws.on_ticks = self._on_ticks
            self.kws.on_connect = self._on_connect
            self.kws.on_close = self._on_close
            self.kws.on_error = self._on_error
            self.kws.connect(threaded=True)
        except Exception as e:
            logger.error(f"Error setting up WebSocket: {str(e)}")

    def _get_access_token(self) -> str:
        """Get stored access token from database"""
        db = SessionLocal()
        try:
            token = db.query(ZerodhaToken).order_by(ZerodhaToken.created_at.desc()).first()
            if not token or self._is_token_expired(token):
                raise Exception("Token expired or not found")
            return token.access_token
        finally:
            db.close()

    def _is_token_expired(self, token: ZerodhaToken) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() >= token.expires_at

    def _on_ticks(self, ws, ticks):
        """Handle incoming ticks"""
        logger.debug(f"Received ticks: {ticks}")

    def _on_connect(self, ws, response):
        """Handle WebSocket connection"""
        logger.info("WebSocket connected")
        # Subscribe to default instruments
        ws.subscribe([256265, 256265])  # Example: NIFTY 50 and BANK NIFTY

    def _on_close(self, ws, code, reason):
        """Handle WebSocket close"""
        logger.info(f"WebSocket closed: {code} - {reason}")

    def _on_error(self, ws, code, reason):
        """Handle WebSocket error"""
        logger.error(f"WebSocket error: {code} - {reason}")

    def get_login_url(self) -> str:
        """Get Zerodha login URL"""
        return self.kite.login_url()

    def generate_session(self, request_token: str) -> Dict:
        """Generate session using request token"""
        try:
            data = self.kite.generate_session(
                request_token,
                api_secret=settings.ZERODHA_API_SECRET
            )
            
            # Store token in database
            db = SessionLocal()
            try:
                token = ZerodhaToken(
                    access_token=data["access_token"],
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                db.add(token)
                db.commit()
            finally:
                db.close()

            return data
        except Exception as e:
            logger.error(f"Error generating session: {str(e)}")
            raise

    def get_historical_data(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day"
    ) -> List[Dict]:
        """Get historical OHLC data"""
        try:
            return self.kite.historical_data(
                instrument_token,
                from_date,
                to_date,
                interval
            )
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise

    def place_paper_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float
    ) -> Dict:
        """Place a paper trade"""
        db = SessionLocal()
        try:
            trade = PaperTrade(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="executed"
            )
            db.add(trade)
            db.commit()
            return trade.to_dict()
        except Exception as e:
            db.rollback()
            logger.error(f"Error placing paper trade: {str(e)}")
            raise
        finally:
            db.close()

    def get_paper_portfolio(self) -> List[Dict]:
        """Get paper trading portfolio"""
        db = SessionLocal()
        try:
            trades = db.query(PaperTrade).all()
            return [trade.to_dict() for trade in trades]
        finally:
            db.close()

    def calculate_pnl(self) -> Dict:
        """Calculate paper trading PnL"""
        db = SessionLocal()
        try:
            trades = db.query(PaperTrade).all()
            total_pnl = 0
            for trade in trades:
                if trade.action == "buy":
                    total_pnl -= trade.price * trade.quantity
                else:
                    total_pnl += trade.price * trade.quantity
            return {"total_pnl": total_pnl}
        finally:
            db.close() 