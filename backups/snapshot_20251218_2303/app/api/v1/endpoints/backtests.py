from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.trading import BacktestResult, Strategy
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_backtests(
    strategy_id: int = None,
    symbol: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's backtests"""
    query = db.query(BacktestResult).join(Strategy).filter(
        Strategy.user_id == current_user.id
    )
    
    if strategy_id:
        query = query.filter(BacktestResult.strategy_id == strategy_id)
    
    if symbol:
        query = query.filter(BacktestResult.symbol == symbol)
    
    backtests = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": b.id,
            "strategy_id": b.strategy_id,
            "symbol": b.symbol,
            "start_date": b.start_date,
            "end_date": b.end_date,
            "initial_balance": b.initial_balance,
            "final_balance": b.final_balance,
            "total_return": b.total_return,
            "sharpe_ratio": b.sharpe_ratio,
            "max_drawdown": b.max_drawdown,
            "win_rate": b.win_rate,
            "metrics": b.metrics,
            "created_at": b.created_at
        }
        for b in backtests
    ]

@router.get("/{backtest_id}", response_model=dict)
def get_backtest(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get backtest by ID"""
    backtest = db.query(BacktestResult).join(Strategy).filter(
        BacktestResult.id == backtest_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return {
        "id": backtest.id,
        "strategy_id": backtest.strategy_id,
        "symbol": backtest.symbol,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_balance": backtest.initial_balance,
        "final_balance": backtest.final_balance,
        "total_return": backtest.total_return,
        "sharpe_ratio": backtest.sharpe_ratio,
        "max_drawdown": backtest.max_drawdown,
        "win_rate": backtest.win_rate,
        "metrics": backtest.metrics,
        "created_at": backtest.created_at
    }

@router.post("/", response_model=dict)
def create_backtest(
    strategy_id: int,
    symbol: str,
    start_date: str,
    end_date: str,
    initial_balance: float,
    final_balance: float,
    total_return: float,
    sharpe_ratio: float,
    max_drawdown: float,
    win_rate: float,
    metrics: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new backtest result"""
    # Verify strategy belongs to user
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    from datetime import datetime
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    backtest = BacktestResult(
        strategy_id=strategy_id,
        symbol=symbol,
        start_date=start_dt,
        end_date=end_dt,
        initial_balance=initial_balance,
        final_balance=final_balance,
        total_return=total_return,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        metrics=metrics
    )
    
    db.add(backtest)
    db.commit()
    db.refresh(backtest)
    
    return {
        "id": backtest.id,
        "strategy_id": backtest.strategy_id,
        "symbol": backtest.symbol,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_balance": backtest.initial_balance,
        "final_balance": backtest.final_balance,
        "total_return": backtest.total_return,
        "sharpe_ratio": backtest.sharpe_ratio,
        "max_drawdown": backtest.max_drawdown,
        "win_rate": backtest.win_rate,
        "metrics": backtest.metrics,
        "created_at": backtest.created_at
    }

@router.get("/strategy/{strategy_id}/summary", response_model=dict)
def get_strategy_backtest_summary(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get backtest summary for strategy"""
    # Verify strategy belongs to user
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    backtests = db.query(BacktestResult).filter(BacktestResult.strategy_id == strategy_id).all()
    
    total_backtests = len(backtests)
    avg_return = sum(b.total_return for b in backtests) / total_backtests if total_backtests > 0 else 0
    avg_sharpe = sum(b.sharpe_ratio for b in backtests) / total_backtests if total_backtests > 0 else 0
    avg_drawdown = sum(b.max_drawdown for b in backtests) / total_backtests if total_backtests > 0 else 0
    
    return {
        "strategy_id": strategy_id,
        "total_backtests": total_backtests,
        "avg_return": avg_return,
        "avg_sharpe_ratio": avg_sharpe,
        "avg_max_drawdown": avg_drawdown
    }

