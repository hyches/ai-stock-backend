from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.trading import Trade
from app.models.database import Portfolio
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_trades(
    portfolio_id: int = None,
    symbol: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's trades"""
    query = db.query(Trade).join(Portfolio).filter(
        Portfolio.user_id == current_user.id
    )
    
    if portfolio_id:
        query = query.filter(Trade.portfolio_id == portfolio_id)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    trades = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "portfolio_id": t.portfolio_id,
            "position_id": t.position_id,
            "symbol": t.symbol,
            "quantity": t.quantity,
            "price": t.price,
            "side": t.side,
            "pnl": t.pnl,
            "fees": t.fees,
            "created_at": t.created_at
        }
        for t in trades
    ]

@router.get("/{trade_id}", response_model=dict)
def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trade by ID"""
    trade = db.query(Trade).join(Portfolio).filter(
        Trade.id == trade_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return {
        "id": trade.id,
        "portfolio_id": trade.portfolio_id,
        "position_id": trade.position_id,
        "symbol": trade.symbol,
        "quantity": trade.quantity,
        "price": trade.price,
        "side": trade.side,
        "pnl": trade.pnl,
        "fees": trade.fees,
        "created_at": trade.created_at
    }

@router.post("/", response_model=dict)
def create_trade(
    portfolio_id: int,
    symbol: str,
    quantity: float,
    price: float,
    side: str,
    position_id: int = None,
    fees: float = 0.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new trade"""
    # Verify portfolio belongs to user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Calculate PnL (simplified)
    pnl = 0.0  # This would be calculated based on position
    
    trade = Trade(
        portfolio_id=portfolio_id,
        position_id=position_id,
        symbol=symbol,
        quantity=quantity,
        price=price,
        side=side,
        pnl=pnl,
        fees=fees
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return {
        "id": trade.id,
        "portfolio_id": trade.portfolio_id,
        "position_id": trade.position_id,
        "symbol": trade.symbol,
        "quantity": trade.quantity,
        "price": trade.price,
        "side": trade.side,
        "pnl": trade.pnl,
        "fees": trade.fees,
        "created_at": trade.created_at
    }

@router.get("/portfolio/{portfolio_id}/summary", response_model=dict)
def get_portfolio_trade_summary(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trade summary for portfolio"""
    # Verify portfolio belongs to user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    trades = db.query(Trade).filter(Trade.portfolio_id == portfolio_id).all()
    
    total_trades = len(trades)
    total_pnl = sum(t.pnl for t in trades)
    total_fees = sum(t.fees for t in trades)
    
    buy_trades = [t for t in trades if t.side == "buy"]
    sell_trades = [t for t in trades if t.side == "sell"]
    
    return {
        "portfolio_id": portfolio_id,
        "total_trades": total_trades,
        "buy_trades": len(buy_trades),
        "sell_trades": len(sell_trades),
        "total_pnl": total_pnl,
        "total_fees": total_fees,
        "net_pnl": total_pnl - total_fees
    }

