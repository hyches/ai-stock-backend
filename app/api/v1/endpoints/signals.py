from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.trading import Signal, Strategy
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_signals(
    strategy_id: int = None,
    symbol: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's signals"""
    query = db.query(Signal).join(Strategy).filter(
        Strategy.user_id == current_user.id
    )
    
    if strategy_id:
        query = query.filter(Signal.strategy_id == strategy_id)
    
    if symbol:
        query = query.filter(Signal.symbol == symbol)
    
    signals = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "strategy_id": s.strategy_id,
            "symbol": s.symbol,
            "signal_type": s.signal_type,
            "confidence": s.confidence,
            "metrics": s.metrics,
            "created_at": s.created_at
        }
        for s in signals
    ]

@router.get("/{signal_id}", response_model=dict)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get signal by ID"""
    signal = db.query(Signal).join(Strategy).filter(
        Signal.id == signal_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return {
        "id": signal.id,
        "strategy_id": signal.strategy_id,
        "symbol": signal.symbol,
        "signal_type": signal.signal_type,
        "confidence": signal.confidence,
        "metrics": signal.metrics,
        "created_at": signal.created_at
    }

@router.post("/", response_model=dict)
def create_signal(
    strategy_id: int,
    symbol: str,
    signal_type: str,
    confidence: float,
    metrics: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new signal"""
    # Verify strategy belongs to user
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    signal = Signal(
        strategy_id=strategy_id,
        symbol=symbol,
        signal_type=signal_type,
        confidence=confidence,
        metrics=metrics
    )
    
    db.add(signal)
    db.commit()
    db.refresh(signal)
    
    return {
        "id": signal.id,
        "strategy_id": signal.strategy_id,
        "symbol": signal.symbol,
        "signal_type": signal.signal_type,
        "confidence": signal.confidence,
        "metrics": signal.metrics,
        "created_at": signal.created_at
    }

@router.get("/strategy/{strategy_id}/summary", response_model=dict)
def get_strategy_signal_summary(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get signal summary for strategy"""
    # Verify strategy belongs to user
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    signals = db.query(Signal).filter(Signal.strategy_id == strategy_id).all()
    
    total_signals = len(signals)
    buy_signals = [s for s in signals if s.signal_type == "buy"]
    sell_signals = [s for s in signals if s.signal_type == "sell"]
    
    avg_confidence = sum(s.confidence for s in signals) / total_signals if total_signals > 0 else 0
    
    return {
        "strategy_id": strategy_id,
        "total_signals": total_signals,
        "buy_signals": len(buy_signals),
        "sell_signals": len(sell_signals),
        "avg_confidence": avg_confidence
    }

