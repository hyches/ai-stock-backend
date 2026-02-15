from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.trading import Strategy
from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyInDB,
    StrategyList
)
from app.services.strategy import StrategyService

router = APIRouter()

@router.get("/", response_model=List[StrategyList])
def list_strategies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Strategy]:
    """List all strategies"""
    strategy_service = StrategyService(db)
    return strategy_service.get_multi(
        skip=skip,
        limit=limit,
        user_id=user_id
    )

@router.post("/", response_model=StrategyInDB)
def create_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_in: StrategyCreate,
    current_user = Depends(deps.get_current_user)
) -> Strategy:
    """Create new strategy"""
    strategy_service = StrategyService(db)
    return strategy_service.create(
        obj_in=strategy_in,
        user_id=current_user.id
    )

@router.get("/{strategy_id}", response_model=StrategyInDB)
def get_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user = Depends(deps.get_current_user)
) -> Strategy:
    """Get strategy by ID"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return strategy

@router.put("/{strategy_id}", response_model=StrategyInDB)
def update_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    strategy_in: StrategyUpdate,
    current_user = Depends(deps.get_current_user)
) -> Strategy:
    """Update strategy"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return strategy_service.update(
        db_obj=strategy,
        obj_in=strategy_in
    )

@router.delete("/{strategy_id}", response_model=StrategyInDB)
def delete_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user = Depends(deps.get_current_user)
) -> Strategy:
    """Delete strategy"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return strategy_service.remove(id=strategy_id)

@router.post("/{strategy_id}/activate")
def activate_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user = Depends(deps.get_current_user)
) -> dict:
    """Activate strategy"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    strategy_service.activate(strategy)
    return {"status": "success", "message": "Strategy activated"}

@router.post("/{strategy_id}/deactivate")
def deactivate_strategy(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    current_user = Depends(deps.get_current_user)
) -> dict:
    """Deactivate strategy"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    strategy_service.deactivate(strategy)
    return {"status": "success", "message": "Strategy deactivated"}

@router.get("/{strategy_id}/performance")
def get_strategy_performance(
    *,
    db: Session = Depends(deps.get_db),
    strategy_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(deps.get_current_user)
) -> dict:
    """Get strategy performance metrics"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.get(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return strategy_service.get_performance(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date
    ) 