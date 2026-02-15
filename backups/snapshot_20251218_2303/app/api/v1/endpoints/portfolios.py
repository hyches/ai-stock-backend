from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.database import Portfolio
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_portfolios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's portfolios"""
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "user_id": p.user_id,
            "created_at": p.created_at,
            "last_updated": p.last_updated,
            "total_value": 100000.0,  # Mock data for now
            "total_change": 5000.0,
            "total_change_percent": 5.0,
            "items": []  # Will be populated with positions
        }
        for p in portfolios
    ]

@router.get("/{portfolio_id}", response_model=dict)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio by ID"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "initial_balance": portfolio.initial_balance,
        "current_balance": portfolio.current_balance,
        "risk_level": portfolio.risk_level,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at
    }

@router.post("/", response_model=dict)
def create_portfolio(
    name: str,
    description: str = None,
    initial_balance: float = 10000.0,
    risk_level: str = "medium",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new portfolio"""
    portfolio = Portfolio(
        name=name,
        description=description,
        initial_balance=initial_balance,
        current_balance=initial_balance,
        risk_level=risk_level,
        user_id=current_user.id
    )
    
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "initial_balance": portfolio.initial_balance,
        "current_balance": portfolio.current_balance,
        "risk_level": portfolio.risk_level,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at
    }

@router.put("/{portfolio_id}", response_model=dict)
def update_portfolio(
    portfolio_id: int,
    name: str = None,
    description: str = None,
    risk_level: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    if name is not None:
        portfolio.name = name
    if description is not None:
        portfolio.description = description
    if risk_level is not None:
        portfolio.risk_level = risk_level
    
    db.commit()
    db.refresh(portfolio)
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "description": portfolio.description,
        "initial_balance": portfolio.initial_balance,
        "current_balance": portfolio.current_balance,
        "risk_level": portfolio.risk_level,
        "created_at": portfolio.created_at,
        "updated_at": portfolio.updated_at
    }

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(portfolio)
    db.commit()
    return {"message": "Portfolio deleted successfully"}

