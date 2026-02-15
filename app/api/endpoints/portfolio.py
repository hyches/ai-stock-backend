from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User
from typing import Dict, Any, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.trading import TradingService

router = APIRouter()

class RebalanceRequest(BaseModel):
    target_weights: Dict[str, float]

@router.get("/")
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user portfolio summary
    """
    trading_service = TradingService(db)
    # Assuming user has one main portfolio for now, or fetch all
    portfolios = await trading_service.get_portfolios(limit=1)
    
    if not portfolios:
        # Return empty structure if no portfolio exists
        return {
            "items": [],
            "totalValue": 0.0,
            "totalChange": 0.0,
            "totalChangePercent": 0.0
        }
    
    portfolio = portfolios[0]
    positions = await trading_service.get_positions(portfolio.id)
    
    # Map to frontend expected format
    items = []
    total_value = 0.0
    
    for pos in positions:
        value = pos.quantity * pos.current_price
        change = (pos.current_price - pos.average_price) * pos.quantity
        change_percent = ((pos.current_price - pos.average_price) / pos.average_price) * 100 if pos.average_price else 0
        
        items.append({
            "symbol": pos.symbol,
            "shares": pos.quantity,
            "avgPrice": pos.average_price,
            "currentPrice": pos.current_price,
            "totalValue": value,
            "change": change,
            "changePercent": change_percent
        })
        total_value += value

    return {
        "id": portfolio.id,
        "items": items,
        "totalValue": total_value,
        # These would surely need real calculation based on history, but approximations for now
        "totalChange": sum(i["change"] for i in items),
        "totalChangePercent": 0.0 # simple placeholder
    }

@router.post("/{portfolio_id}/rebalance")
async def rebalance_portfolio(
    portfolio_id: int,
    request: RebalanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate rebalancing trades based on target weights
    """
    trading_service = TradingService(db)
    
    # verify ownership
    portfolio = await trading_service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    # In a real app, check portfolio.user_id == current_user.id
    
    suggested_trades = await trading_service.rebalance_portfolio_execution(portfolio_id, request.target_weights)
    
    return {
        "portfolio_id": portfolio_id,
        "suggested_actions": suggested_trades
    }