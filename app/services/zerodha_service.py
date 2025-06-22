from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import json
import websockets
import asyncio
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.zerodha import ZerodhaToken, PaperTrade
from app.core.cache import redis_cache
from app.services.market_data_service import MarketDataService
from app.services.broker_base import BrokerBase

logger = logging.getLogger(__name__)

class ZerodhaService(BrokerBase):
    def __init__(self):
        super().__init__()
        self.api_key = settings.ZERODHA_API_KEY
        self.api_secret = settings.ZERODHA_API_SECRET
        self.ws_url = "wss://ws.kite.trade"
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1  # seconds
        self.heartbeat_interval = 30  # seconds
        self.message_queue = asyncio.Queue()
        self.market_data_service = MarketDataService()
        self.use_alternative_data = not (self.api_key and self.api_secret)
        if not self.use_alternative_data:
            self._setup_websocket()

    async def login(self, *args, **kwargs):
        """Placeholder for login functionality."""
        logger.info("Login method called, but not implemented.")
        return {"status": "login required", "login_url": await self.get_login_url()}

    async def place_order(self, *args, **kwargs):
        """Placeholder for order placement."""
        logger.info("Place order method called, but not implemented.")
        # This would be replaced with actual order placement logic
        # For now, we simulate a paper trade
        return await self.place_paper_trade(*args, **kwargs)

    async def get_portfolio(self, *args, **kwargs):
        """Placeholder for fetching the portfolio."""
        logger.info("Get portfolio method called, using paper portfolio.")
        return await self.get_paper_portfolio()

    async def get_quote(self, *args, **kwargs):
        """Placeholder for fetching a quote."""
        logger.info("Get quote method called, using live quote implementation.")
        return await self.get_live_quote(*args, **kwargs)

    async def _setup_websocket(self):
        """Setup WebSocket connection for MCP"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.ws = await websockets.connect(self.ws_url)
                self.connected = True
                self.reconnect_attempts = 0
                await self._authenticate()
                await self._subscribe_to_default_instruments()
                asyncio.create_task(self._start_heartbeat())
                asyncio.create_task(self._process_message_queue())
                break
            except Exception as e:
                logger.error(f"Error setting up WebSocket: {str(e)}")
                self.reconnect_attempts += 1
                await asyncio.sleep(self.reconnect_delay * self.reconnect_attempts)

    async def _start_heartbeat(self):
        """Start heartbeat mechanism"""
        while self.connected:
            try:
                await self.ws.send(json.dumps({"type": "ping"}))
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                await self._handle_connection_error()

    async def _handle_connection_error(self):
        """Handle connection errors"""
        self.connected = False
        if self.ws:
            await self.ws.close()
        await self._setup_websocket()

    async def _process_message_queue(self):
        """Process messages from queue"""
        while self.connected:
            try:
                message = await self.message_queue.get()
                await self._handle_message(message)
                self.message_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")

    async def _handle_message(self, message: Dict):
        """Handle incoming WebSocket messages"""
        try:
            if message.get("type") == "quote":
                await self._handle_quote(message)
            elif message.get("type") == "error":
                await self._handle_error(message)
            elif message.get("type") == "pong":
                logger.debug("Received pong")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")

    async def _handle_quote(self, quote: Dict):
        """Handle quote updates"""
        try:
            await redis_cache.set(
                f"quote:{quote['instrument_token']}",
                quote,
                expire=60
            )
        except Exception as e:
            logger.error(f"Error handling quote: {str(e)}")

    async def _handle_error(self, error: Dict):
        """Handle error messages"""
        logger.error(f"WebSocket error: {error}")
        if error.get("code") in ["auth_failed", "token_expired"]:
            await self._handle_connection_error()

    async def _authenticate(self):
        """Authenticate with MCP"""
        auth_message = {
            "type": "auth",
            "api_key": self.api_key,
            "api_secret": self.api_secret
        }
        await self.ws.send(json.dumps(auth_message))
        response = await self.ws.recv()
        auth_response = json.loads(response)
        if auth_response.get("status") != "success":
            raise Exception("MCP authentication failed")

    async def _subscribe_to_default_instruments(self):
        """Subscribe to default instruments"""
        subscribe_message = {
            "type": "subscribe",
            "instruments": [
                {"instrument_token": 256265, "type": "quote"},
                {"instrument_token": 260105, "type": "quote"}
            ]
        }
        await self.ws.send(json.dumps(subscribe_message))

    async def _get_access_token(self) -> str:
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

    async def get_login_url(self) -> str:
        """Get Zerodha login URL for MCP"""
        return f"https://kite.trade/connect/login?api_key={self.api_key}"

    async def generate_session(self, request_token: str) -> Dict:
        """Generate session using request token"""
        try:
            auth_message = {
                "type": "auth",
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "request_token": request_token
            }
            await self.ws.send(json.dumps(auth_message))
            response = await self.ws.recv()
            session_data = json.loads(response)
            
            if session_data.get("status") != "success":
                raise Exception("Session generation failed")

            db = SessionLocal()
            try:
                token = ZerodhaToken(
                    access_token=session_data["access_token"],
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                db.add(token)
                db.commit()
            finally:
                db.close()

            return session_data
        except Exception as e:
            logger.error(f"Error generating session: {str(e)}")
            raise

    async def get_historical_data(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day"
    ) -> List[Dict]:
        """Get historical OHLC data"""
        try:
            if self.use_alternative_data:
                symbol = await self._get_symbol_from_token(instrument_token)
                return await self.market_data_service.get_historical_data(
                    symbol,
                    from_date,
                    to_date,
                    interval
                )
            else:
                request = {
                    "type": "historical",
                    "instrument_token": instrument_token,
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat(),
                    "interval": interval
                }
                await self.ws.send(json.dumps(request))
                response = await self.ws.recv()
                return json.loads(response)["data"]
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise

    async def _get_symbol_from_token(self, instrument_token: int) -> str:
        """Get symbol from instrument token"""
        token_to_symbol = {
            256265: "NIFTY 50",
            260105: "BANK NIFTY",
        }
        return token_to_symbol.get(instrument_token, "NIFTY 50")

    async def get_live_quote(self, symbol: str) -> Dict:
        """Get live quote"""
        try:
            if self.use_alternative_data:
                return await self.market_data_service.get_live_quote(symbol)
            else:
                instrument_token = await self._get_instrument_token(symbol)
                if not instrument_token:
                    raise Exception(f"Invalid symbol: {symbol}")

                cache_key = f"quote:{instrument_token}"
                cached_quote = await redis_cache.get(cache_key)
                if cached_quote:
                    return cached_quote

                subscribe_message = {
                    "type": "subscribe",
                    "instruments": [
                        {"instrument_token": instrument_token, "type": "quote"}
                    ]
                }
                await self.ws.send(json.dumps(subscribe_message))

                response = await asyncio.wait_for(self.ws.recv(), timeout=5)
                quote_data = json.loads(response)
                await redis_cache.set(cache_key, quote_data, expire=60)
                return quote_data
        except Exception as e:
            logger.error(f"Error getting live quote for {symbol}: {str(e)}")
            raise

    async def _get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token from symbol"""
        # This is a placeholder
        symbol_to_token = {
            "NIFTY 50": 256265,
            "BANK NIFTY": 260105,
        }
        return symbol_to_token.get(symbol.upper())

    async def place_paper_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float
    ) -> Dict:
        """Place a paper trade and store it in the database"""
        db = SessionLocal()
        try:
            trade = PaperTrade(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price
            )
            db.add(trade)
            db.commit()
            return {"status": "success", "trade_id": trade.id}
        finally:
            db.close()

    async def get_paper_portfolio(self) -> List[Dict]:
        """Get paper trading portfolio"""
        db = SessionLocal()
        try:
            trades = db.query(PaperTrade).all()
            return [
                {
                    "symbol": t.symbol,
                    "action": t.action,
                    "quantity": t.quantity,
                    "price": t.price,
                    "timestamp": t.timestamp
                }
                for t in trades
            ]
        finally:
            db.close()

    async def calculate_pnl(self) -> Dict:
        """Calculate PnL for paper trades"""
        portfolio = await self.get_paper_portfolio()
        total_pnl = 0
        
        for trade in portfolio:
            current_price = (await self.get_live_quote(trade["symbol"]))["price"]
            if trade["action"] == "buy":
                pnl = (current_price - trade["price"]) * trade["quantity"]
            else:
                pnl = (trade["price"] - current_price) * trade["quantity"]
            total_pnl += pnl
            
        return {"total_pnl": total_pnl, "portfolio": portfolio} 