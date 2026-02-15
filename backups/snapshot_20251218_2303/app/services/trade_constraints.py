from typing import Dict, Optional
from decimal import Decimal
from app.db.session import SessionLocal
from app.models.zerodha import PaperTrade
from app.core.config import settings

class TradeConstraints:
    def __init__(self):
        self.max_position_size = Decimal('1000000')  # 1M
        self.max_trade_size = Decimal('100000')      # 100K
        self.min_trade_size = Decimal('1000')        # 1K
        self.max_leverage = Decimal('5')             # 5x
        self.max_daily_trades = 50
        self.max_open_positions = 10

    def validate_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        user_id: int
    ) -> Dict:
        """Validate trade against constraints"""
        errors = []
        
        # Calculate trade value
        trade_value = Decimal(str(quantity)) * Decimal(str(price))
        
        # Check trade size
        if trade_value > self.max_trade_size:
            errors.append(f"Trade value {trade_value} exceeds maximum {self.max_trade_size}")
        if trade_value < self.min_trade_size:
            errors.append(f"Trade value {trade_value} below minimum {self.min_trade_size}")

        # Check position size
        current_position = self._get_current_position(symbol, user_id)
        new_position = current_position + (trade_value if action == "buy" else -trade_value)
        if abs(new_position) > self.max_position_size:
            errors.append(f"New position size {new_position} exceeds maximum {self.max_position_size}")

        # Check daily trade limit
        if self._get_daily_trade_count(user_id) >= self.max_daily_trades:
            errors.append(f"Daily trade limit of {self.max_daily_trades} reached")

        # Check open positions limit
        if action == "buy" and self._get_open_positions_count(user_id) >= self.max_open_positions:
            errors.append(f"Maximum open positions limit of {self.max_open_positions} reached")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def _get_current_position(self, symbol: str, user_id: int) -> Decimal:
        """Get current position size for symbol"""
        db = SessionLocal()
        try:
            trades = db.query(PaperTrade).filter(
                PaperTrade.symbol == symbol,
                PaperTrade.user_id == user_id
            ).all()
            
            position = Decimal('0')
            for trade in trades:
                if trade.action == "buy":
                    position += Decimal(str(trade.quantity)) * Decimal(str(trade.price))
                else:
                    position -= Decimal(str(trade.quantity)) * Decimal(str(trade.price))
            return position
        finally:
            db.close()

    def _get_daily_trade_count(self, user_id: int) -> int:
        """Get number of trades today"""
        db = SessionLocal()
        try:
            return db.query(PaperTrade).filter(
                PaperTrade.user_id == user_id,
                PaperTrade.created_at >= datetime.utcnow().date()
            ).count()
        finally:
            db.close()

    def _get_open_positions_count(self, user_id: int) -> int:
        """Get number of open positions"""
        db = SessionLocal()
        try:
            positions = db.query(PaperTrade.symbol).filter(
                PaperTrade.user_id == user_id
            ).distinct().count()
            return positions
        finally:
            db.close()

trade_constraints = TradeConstraints() 