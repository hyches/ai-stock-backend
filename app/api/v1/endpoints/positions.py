from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.trading import Position
from app.models.database import Portfolio
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_positions(
    portfolio_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's positions"""
    query = db.query(Position).join(Portfolio).filter(
        Portfolio.user_id == current_user.id
    )
    
    if portfolio_id:
        query = query.filter(Position.portfolio_id == portfolio_id)
    
    positions = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "portfolio_id": p.portfolio_id,
            "symbol": p.symbol,
            "quantity": p.quantity,
            "average_price": p.average_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "realized_pnl": p.realized_pnl,
            "stop_loss": p.stop_loss,
            "take_profit": p.take_profit,
            "status": p.status,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in positions
    ]

@router.get("/{position_id}", response_model=dict)
def get_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get position by ID"""
    position = db.query(Position).join(Portfolio).filter(
        Position.id == position_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return {
        "id": position.id,
        "portfolio_id": position.portfolio_id,
        "symbol": position.symbol,
        "quantity": position.quantity,
        "average_price": position.average_price,
        "current_price": position.current_price,
        "unrealized_pnl": position.unrealized_pnl,
        "realized_pnl": position.realized_pnl,
        "stop_loss": position.stop_loss,
        "take_profit": position.take_profit,
        "status": position.status,
        "created_at": position.created_at,
        "updated_at": position.updated_at
    }

@router.post("/", response_model=dict)
def create_position(
    portfolio_id: int,
    symbol: str,
    quantity: float,
    average_price: float,
    current_price: float,
    stop_loss: float = None,
    take_profit: float = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new position"""
    # Verify portfolio belongs to user
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Calculate PnL
    unrealized_pnl = (current_price - average_price) * quantity
    
    position = Position(
        portfolio_id=portfolio_id,
        symbol=symbol,
        quantity=quantity,
        average_price=average_price,
        current_price=current_price,
        unrealized_pnl=unrealized_pnl,
        realized_pnl=0.0,
        stop_loss=stop_loss,
        take_profit=take_profit,
        status="open"
    )
    
    db.add(position)
    db.commit()
    db.refresh(position)
    
    return {
        "id": position.id,
        "portfolio_id": position.portfolio_id,
        "symbol": position.symbol,
        "quantity": position.quantity,
        "average_price": position.average_price,
        "current_price": position.current_price,
        "unrealized_pnl": position.unrealized_pnl,
        "realized_pnl": position.realized_pnl,
        "stop_loss": position.stop_loss,
        "take_profit": position.take_profit,
        "status": position.status,
        "created_at": position.created_at,
        "updated_at": position.updated_at
    }

@router.put("/{position_id}", response_model=dict)
def update_position(
    position_id: int,
    current_price: float = None,
    stop_loss: float = None,
    take_profit: float = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update position"""
    position = db.query(Position).join(Portfolio).filter(
        Position.id == position_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if current_price is not None:
        position.current_price = current_price
        position.unrealized_pnl = (current_price - position.average_price) * position.quantity
    
    if stop_loss is not None:
        position.stop_loss = stop_loss
    
    if take_profit is not None:
        position.take_profit = take_profit
    
    if status is not None:
        position.status = status
    
    db.commit()
    db.refresh(position)
    
    return {
        "id": position.id,
        "portfolio_id": position.portfolio_id,
        "symbol": position.symbol,
        "quantity": position.quantity,
        "average_price": position.average_price,
        "current_price": position.current_price,
        "unrealized_pnl": position.unrealized_pnl,
        "realized_pnl": position.realized_pnl,
        "stop_loss": position.stop_loss,
        "take_profit": position.take_profit,
        "status": position.status,
        "created_at": position.created_at,
        "updated_at": position.updated_at
    }

@router.delete("/{position_id}")
def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete position"""
    position = db.query(Position).join(Portfolio).filter(
        Position.id == position_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    db.delete(position)
    db.commit()
    return {"message": "Position deleted successfully"}

