from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.order_executor import OrderExecutor, OrderSide, OrderType
from datetime import datetime

router = APIRouter()
executor = OrderExecutor()
executor.start() # Start simulation thread

class AdvancedOrderRequest(BaseModel):
    symbol: str
    side: str # BUY or SELL
    order_type: str # MARKET, LIMIT, BRACKET, TRAILING_STOP
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    trail_percent: Optional[float] = None

@router.post("/advanced-order")
async def submit_advanced_order(order: AdvancedOrderRequest):
    """
    Institutional execution routing.
    Calls the hidden 'OrderExecutor' service to handle complex types.
    """
    try:
        side = OrderSide.BUY if order.side.upper() == "BUY" else OrderSide.SELL
        
        if order.order_type == "BRACKET":
            if not order.target_price or not order.stop_price or not order.price:
                raise HTTPException(status_code=400, detail="Bracket orders require price, target, and stop loss.")
            
            bracket = executor.create_bracket_order(
                symbol=order.symbol,
                side=side,
                quantity=order.quantity,
                entry_price=order.price,
                target_price=order.target_price,
                stop_loss_price=order.stop_price
            )
            return {"status": "OPEN", "order_id": bracket.entry_order.id, "type": "BRACKET"}
            
        elif order.order_type == "TRAILING_STOP":
            if not order.trail_percent:
                raise HTTPException(status_code=400, detail="Trailing stop requires trail_percent.")
                
            ts_order = executor.create_trailing_stop(
                symbol=order.symbol,
                side=side,
                quantity=order.quantity,
                trail_percent=order.trail_percent
            )
            return {"status": "OPEN", "order_id": ts_order.order.id, "type": "TRAILING_STOP"}
            
        elif order.order_type == "LIMIT":
            res = executor.create_limit_order(order.symbol, side, order.quantity, order.price)
            return {"status": "OPEN", "order_id": res.id, "type": "LIMIT"}
            
        else: # Default Market
            res = executor.create_market_order(order.symbol, side, order.quantity)
            return {"status": "FILLED", "order_id": res.id, "type": "MARKET"}
            
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_pro_orders():
    """Get orders from the professional execution engine"""
    return [order.to_dict() for order in executor.get_open_orders()]
