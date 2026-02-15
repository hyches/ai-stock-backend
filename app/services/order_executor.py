"""
Advanced Order Execution Engine
Supports bracket orders, trailing stops, OCO, and realistic fill simulation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LOSS_LIMIT = "stop_loss_limit"
    TRAILING_STOP = "trailing_stop"
    BRACKET = "bracket"
    OCO = "oco"  # One-Cancels-Other
    ICEBERG = "iceberg"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(Enum):
    DAY = "day"
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


@dataclass
class Order:
    """Base order structure"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.DAY
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_fill_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    parent_order_id: Optional[str] = None
    child_order_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'time_in_force': self.time_in_force.value,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'average_fill_price': self.average_fill_price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parent_order_id': self.parent_order_id,
            'child_order_ids': self.child_order_ids,
            'metadata': self.metadata
        }


@dataclass
class BracketOrder:
    """Bracket order with entry, target, and stop loss"""
    entry_order: Order
    target_order: Order
    stop_loss_order: Order
    
    def get_all_orders(self) -> List[Order]:
        return [self.entry_order, self.target_order, self.stop_loss_order]


@dataclass
class TrailingStopOrder:
    """Trailing stop loss order"""
    order: Order
    trail_amount: float  # Absolute amount
    trail_percent: Optional[float] = None  # Percentage
    highest_price: float = 0.0  # For buy side trailing
    lowest_price: float = float('inf')  # For sell side trailing


class OrderExecutor:
    """
    Advanced order execution engine with realistic fill simulation
    """
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.bracket_orders: Dict[str, BracketOrder] = {}
        self.trailing_stops: Dict[str, TrailingStopOrder] = {}
        self.order_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Execution parameters
        self.slippage_model = "volatility"  # or "fixed"
        self.fixed_slippage_bps = 5  # 5 basis points
        self.commission_bps = 3  # 3 basis points
        
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the order executor"""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_orders())
        logger.info("Order Executor started")
    
    async def stop(self):
        """Stop the order executor"""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
        logger.info("Order Executor stopped")
    
    def create_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Order:
        """Create a market order"""
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            time_in_force=time_in_force,
            status=OrderStatus.PENDING
        )
        
        self.orders[order.id] = order
        logger.info(f"Created market order: {order.id}")
        return order
    
    def create_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Order:
        """Create a limit order"""
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            status=OrderStatus.PENDING
        )
        
        self.orders[order.id] = order
        logger.info(f"Created limit order: {order.id}")
        return order
    
    def create_bracket_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        entry_price: float,
        target_price: float,
        stop_loss_price: float
    ) -> BracketOrder:
        """
        Create a bracket order with entry, target, and stop loss
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            entry_price: Entry limit price
            target_price: Target profit price
            stop_loss_price: Stop loss price
        """
        # Entry order
        entry_order = self.create_limit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=entry_price,
            time_in_force=TimeInForce.GTC
        )
        
        # Target order (opposite side)
        target_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
        target_order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=target_side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=target_price,
            time_in_force=TimeInForce.GTC,
            status=OrderStatus.PENDING,
            parent_order_id=entry_order.id,
            metadata={'bracket_leg': 'target'}
        )
        
        # Stop loss order (opposite side)
        stop_loss_order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=target_side,
            order_type=OrderType.STOP_LOSS,
            quantity=quantity,
            stop_price=stop_loss_price,
            time_in_force=TimeInForce.GTC,
            status=OrderStatus.PENDING,
            parent_order_id=entry_order.id,
            metadata={'bracket_leg': 'stop_loss'}
        )
        
        # Link orders
        entry_order.child_order_ids = [target_order.id, stop_loss_order.id]
        
        # Store all orders
        self.orders[target_order.id] = target_order
        self.orders[stop_loss_order.id] = stop_loss_order
        
        bracket = BracketOrder(
            entry_order=entry_order,
            target_order=target_order,
            stop_loss_order=stop_loss_order
        )
        
        self.bracket_orders[entry_order.id] = bracket
        logger.info(f"Created bracket order: {entry_order.id}")
        
        return bracket
    
    def create_trailing_stop(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        trail_percent: float,
        trail_amount: Optional[float] = None
    ) -> TrailingStopOrder:
        """
        Create a trailing stop loss order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            trail_percent: Trailing percentage (e.g., 2.0 for 2%)
            trail_amount: Trailing amount in absolute terms
        """
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            order_type=OrderType.TRAILING_STOP,
            quantity=quantity,
            time_in_force=TimeInForce.GTC,
            status=OrderStatus.PENDING,
            metadata={'trail_percent': trail_percent, 'trail_amount': trail_amount}
        )
        
        self.orders[order.id] = order
        
        trailing_stop = TrailingStopOrder(
            order=order,
            trail_amount=trail_amount or 0,
            trail_percent=trail_percent
        )
        
        self.trailing_stops[order.id] = trailing_stop
        logger.info(f"Created trailing stop: {order.id}")
        
        return trailing_stop
    
    async def submit_order(self, order_id: str) -> bool:
        """
        Submit an order for execution
        
        Args:
            order_id: Order ID to submit
        """
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        order.status = OrderStatus.OPEN
        order.updated_at = datetime.utcnow()
        
        # Trigger callbacks
        await self._trigger_callbacks(order_id, 'submitted')
        
        logger.info(f"Submitted order: {order_id}")
        return True
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        
        # If bracket order, cancel child orders
        if order_id in self.bracket_orders:
            bracket = self.bracket_orders[order_id]
            for child_order in [bracket.target_order, bracket.stop_loss_order]:
                await self.cancel_order(child_order.id)
        
        await self._trigger_callbacks(order_id, 'cancelled')
        
        logger.info(f"Cancelled order: {order_id}")
        return True
    
    async def simulate_fill(
        self,
        order_id: str,
        market_price: float,
        market_volume: int,
        volatility: float = 0.01
    ) -> bool:
        """
        Simulate realistic order fill
        
        Args:
            order_id: Order to fill
            market_price: Current market price
            market_volume: Available market volume
            volatility: Current volatility (for slippage calculation)
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        if order.status not in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
            return False
        
        # Check if order should be filled
        should_fill, fill_price = self._should_fill_order(order, market_price)
        
        if not should_fill:
            return False
        
        # Calculate slippage
        slippage = self._calculate_slippage(order, market_price, volatility)
        fill_price += slippage
        
        # Determine fill quantity (partial fills for large orders)
        remaining_qty = order.quantity - order.filled_quantity
        fill_qty = min(remaining_qty, market_volume)
        
        # Update order
        total_value = (order.average_fill_price * order.filled_quantity) + (fill_price * fill_qty)
        order.filled_quantity += fill_qty
        order.average_fill_price = total_value / order.filled_quantity
        
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        order.updated_at = datetime.utcnow()
        
        # Handle bracket order logic
        if order.parent_order_id is None and order_id in self.bracket_orders:
            # Entry order filled, activate child orders
            bracket = self.bracket_orders[order_id]
            await self.submit_order(bracket.target_order.id)
            await self.submit_order(bracket.stop_loss_order.id)
        
        elif order.parent_order_id and order.status == OrderStatus.FILLED:
            # Child order filled, cancel sibling
            parent_id = order.parent_order_id
            if parent_id in self.bracket_orders:
                bracket = self.bracket_orders[parent_id]
                for child in [bracket.target_order, bracket.stop_loss_order]:
                    if child.id != order_id:
                        await self.cancel_order(child.id)
        
        await self._trigger_callbacks(order_id, 'filled')
        
        logger.info(f"Filled order {order_id}: {fill_qty} @ {fill_price:.2f}")
        return True
    
    def _should_fill_order(self, order: Order, market_price: float) -> tuple[bool, float]:
        """Determine if order should be filled and at what price"""
        if order.order_type == OrderType.MARKET:
            return True, market_price
        
        elif order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and market_price <= order.price:
                return True, order.price
            elif order.side == OrderSide.SELL and market_price >= order.price:
                return True, order.price
        
        elif order.order_type == OrderType.STOP_LOSS:
            if order.side == OrderSide.BUY and market_price >= order.stop_price:
                return True, market_price
            elif order.side == OrderSide.SELL and market_price <= order.stop_price:
                return True, market_price
        
        return False, 0.0
    
    def _calculate_slippage(self, order: Order, market_price: float, volatility: float) -> float:
        """Calculate realistic slippage"""
        if self.slippage_model == "fixed":
            slippage_pct = self.fixed_slippage_bps / 10000
        else:  # volatility-based
            slippage_pct = volatility * 0.5  # Half of volatility
        
        slippage = market_price * slippage_pct
        
        # Slippage direction
        if order.side == OrderSide.BUY:
            return slippage  # Pay more
        else:
            return -slippage  # Receive less
    
    async def _monitor_orders(self):
        """Monitor and update trailing stops"""
        while self._running:
            try:
                # Update trailing stops
                for order_id, trailing_stop in list(self.trailing_stops.items()):
                    # This would need real-time price feed
                    # For now, it's a placeholder
                    pass
                
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Order monitor error: {e}")
    
    def update_trailing_stop(self, order_id: str, current_price: float):
        """Update trailing stop based on current price"""
        if order_id not in self.trailing_stops:
            return
        
        trailing = self.trailing_stops[order_id]
        order = trailing.order
        
        if order.side == OrderSide.SELL:
            # Trailing for long position
            if current_price > trailing.highest_price:
                trailing.highest_price = current_price
                
                # Update stop price
                if trailing.trail_percent:
                    new_stop = current_price * (1 - trailing.trail_percent / 100)
                else:
                    new_stop = current_price - trailing.trail_amount
                
                order.stop_price = new_stop
                order.updated_at = datetime.utcnow()
                logger.info(f"Updated trailing stop {order_id}: {new_stop:.2f}")
        
        else:  # BUY side (trailing for short position)
            if current_price < trailing.lowest_price:
                trailing.lowest_price = current_price
                
                if trailing.trail_percent:
                    new_stop = current_price * (1 + trailing.trail_percent / 100)
                else:
                    new_stop = current_price + trailing.trail_amount
                
                order.stop_price = new_stop
                order.updated_at = datetime.utcnow()
    
    def register_callback(self, order_id: str, callback: Callable):
        """Register a callback for order events"""
        self.order_callbacks[order_id].append(callback)
    
    async def _trigger_callbacks(self, order_id: str, event: str):
        """Trigger callbacks for an order event"""
        if order_id in self.order_callbacks:
            for callback in self.order_callbacks[order_id]:
                try:
                    await callback(self.orders[order_id], event)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID"""
        return self.orders.get(order_id)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders, optionally filtered by symbol"""
        orders = [
            o for o in self.orders.values()
            if o.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
        ]
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        return orders
    
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Order]:
        """Get order history"""
        orders = list(self.orders.values())
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        # Sort by created_at descending
        orders.sort(key=lambda x: x.created_at, reverse=True)
        
        return orders[:limit]


# Singleton instance
order_executor = OrderExecutor()
